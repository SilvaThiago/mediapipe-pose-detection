"""Main entry point for Multi-Camera Motion Capture System."""

import tkinter as tk
from Models.MultiCameraExperimentModel import MultiCameraExperimentModel
from Views.MultiCameraExperimentView import MultiCameraExperimentView
from Controls.MultiCameraExperimentController import MultiCameraExperimentController


def main():
    """Main function to start the application."""
    
    # Create root window
    root = tk.Tk()
    
    # Create MVC components
    model = MultiCameraExperimentModel()
    view = MultiCameraExperimentView(root)
    controller = MultiCameraExperimentController(view, model)
    
    # Handle window close event
    def on_closing():
        """Handle application close."""
        print("Closing application...")
        controller.cleanup()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Start main loop
    print("Starting Multi-Camera Motion Capture System...")
    root.mainloop()


if __name__ == "__main__":
    main()