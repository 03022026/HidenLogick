"""Performance metrics overlay for Minecraft."""
import os
import psutil
import threading
import time
from typing import Callable


class PerformanceMetrics:
    """Monitor and collect performance metrics."""
    
    def __init__(self, update_interval: float = 1.0):
        self.update_interval = update_interval
        self.monitoring = False
        self.monitor_thread = None
        
        # Metrics
        self.fps = 0
        self.cpu_usage = 0
        self.ram_usage = 0
        self.ram_used_mb = 0
        self.ram_total_mb = 0
        self.gpu_usage = 0
        self.process = None
        
        self.callbacks = []  # For UI updates
    
    def register_callback(self, callback: Callable):
        """Register a callback to be called when metrics update."""
        self.callbacks.append(callback)
    
    def start_monitoring(self, process_pid: int = None):
        """Start monitoring performance metrics."""
        if self.monitoring:
            return
        
        try:
            if process_pid:
                self.process = psutil.Process(process_pid)
            else:
                self.process = psutil.Process()
        except:
            print("Failed to get process handle")
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop monitoring performance metrics."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
    
    def _monitor_loop(self):
        """Main monitoring loop (runs in background thread)."""
        while self.monitoring:
            try:
                # CPU usage
                if self.process:
                    try:
                        self.cpu_usage = self.process.cpu_percent(interval=0.1)
                    except:
                        self.cpu_usage = psutil.cpu_percent(interval=0.1)
                else:
                    self.cpu_usage = psutil.cpu_percent(interval=0.1)
                
                # Memory usage
                if self.process:
                    try:
                        mem_info = self.process.memory_info()
                        self.ram_used_mb = mem_info.rss / (1024 * 1024)
                    except:
                        self.ram_used_mb = 0
                
                # System RAM
                ram_info = psutil.virtual_memory()
                self.ram_total_mb = ram_info.total / (1024 * 1024)
                self.ram_usage = ram_info.percent
                
                # Estimate FPS (based on process responsiveness)
                # This is a rough estimate; real FPS requires game output parsing
                self.fps = self._estimate_fps()
                
                # Trigger callbacks
                for callback in self.callbacks:
                    try:
                        callback(self.get_metrics())
                    except:
                        pass
                
                time.sleep(self.update_interval)
            except Exception as e:
                print(f"Metrics collection error: {e}")
                time.sleep(1)
    
    def _estimate_fps(self, base_fps: int = 60) -> int:
        """Estimate FPS based on CPU usage.
        
        This is a rough approximation. Real FPS requires game output parsing.
        """
        if self.cpu_usage < 20:
            return base_fps
        elif self.cpu_usage < 50:
            return int(base_fps * 0.9)
        elif self.cpu_usage < 80:
            return int(base_fps * 0.7)
        else:
            return int(base_fps * 0.5)
    
    def get_metrics(self) -> dict:
        """Get current metrics snapshot."""
        return {
            'fps': self.fps,
            'cpu_usage': round(self.cpu_usage, 1),
            'ram_usage': round(self.ram_usage, 1),
            'ram_used_mb': round(self.ram_used_mb, 1),
            'ram_total_mb': round(self.ram_total_mb, 0),
            'timestamp': time.time()
        }
    
    def get_formatted_metrics(self) -> str:
        """Get formatted metrics string for display."""
        metrics = self.get_metrics()
        return (
            f"FPS: {metrics['fps']} | "
            f"CPU: {metrics['cpu_usage']}% | "
            f"RAM: {metrics['ram_used_mb']}MB / {metrics['ram_total_mb']}MB ({metrics['ram_usage']}%)"
        )


class PerformanceOverlay:
    """Visual overlay for performance metrics (can be shown in-game or in launcher)."""
    
    def __init__(self, metrics: PerformanceMetrics):
        self.metrics = metrics
        self.visible = False
        self.position = (10, 10)  # Top-left corner
    
    def toggle(self):
        """Toggle overlay visibility."""
        self.visible = not self.visible
    
    def get_overlay_text(self) -> str:
        """Get text to display in overlay."""
        return self.metrics.get_formatted_metrics()
    
    def get_overlay_data(self) -> dict:
        """Get overlay positioning and styling data."""
        return {
            'position': self.position,
            'visible': self.visible,
            'background_color': '#00000080',  # Semi-transparent black
            'text_color': '#00ff00',  # Bright green
            'font_size': 12,
            'font_family': 'monospace',
            'text': self.get_overlay_text()
        }


class PerformanceLogger:
    """Log performance metrics to file."""
    
    def __init__(self, log_dir: str):
        self.log_dir = log_dir
        self.log_file = None
        self.logging = False
    
    def start_logging(self, session_name: str = "performance"):
        """Start logging metrics to file."""
        os.makedirs(self.log_dir, exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(self.log_dir, f"{session_name}_{timestamp}.json")
        self.logging = True
        
        with open(self.log_file, 'w') as f:
            f.write("[\n")
    
    def log_metrics(self, metrics: dict):
        """Log a metrics snapshot."""
        if not self.logging or not self.log_file:
            return
        
        try:
            import json
            with open(self.log_file, 'a') as f:
                json.dump(metrics, f)
                f.write(",\n")
        except:
            pass
    
    def stop_logging(self):
        """Stop logging metrics."""
        if self.logging and self.log_file:
            try:
                with open(self.log_file, 'a') as f:
                    f.write("{}]\n")  # Close JSON array
            except:
                pass
            self.logging = False
