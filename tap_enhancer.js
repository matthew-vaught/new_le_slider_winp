// iPad Tap Enhancer
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on a touch device
    const isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
    
    if (isTouchDevice) {
        console.log("Touch device detected - enhancing visualization");
        
        // Wait for Bokeh to initialize
        setTimeout(function() {
            // Find the canvas element
            const canvases = document.querySelectorAll('.bk-canvas-events');
            
            // Create a div to display team info
            const infoDiv = document.createElement('div');
            infoDiv.id = 'team-info';
            infoDiv.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background-color: white;
                border: 2px solid #3498db;
                border-radius: 5px;
                padding: 10px;
                box-shadow: 0 3px 10px rgba(0,0,0,0.2);
                z-index: 1000;
                min-width: 150px;
                text-align: center;
                font-family: Arial, sans-serif;
                display: none;
            `;
            document.body.appendChild(infoDiv);
            
            // Process each canvas
            canvases.forEach(function(canvas) {
                console.log("Enhancing canvas for tap events");
                
                // Set touch-action to none to prevent scrolling
                canvas.style.touchAction = 'none';
                
                // Add touch event listener
                canvas.addEventListener('touchend', function(e) {
                    // Prevent default to avoid zoom/scroll behaviors
                    e.preventDefault();
                    
                    // Get the touch coordinates
                    const touch = e.changedTouches[0];
                    
                    // First dispatch a click event to trigger Bokeh's selection
                    const clickEvent = new MouseEvent('click', {
                        bubbles: true,
                        cancelable: true,
                        view: window,
                        clientX: touch.clientX,
                        clientY: touch.clientY
                    });
                    canvas.dispatchEvent(clickEvent);
                    
                    // Wait a moment for Bokeh to process the selection
                    setTimeout(function() {
                        // Find the selected point (it will have a different style)
                        const selectedPoints = document.querySelectorAll('.bk-canvas .bk-selected');
                        
                        if (selectedPoints.length > 0) {
                            // Try to get the data from the tooltip if visible
                            const tooltips = document.querySelectorAll('.bk-tooltip-content');
                            
                            if (tooltips.length > 0) {
                                // Extract data from the tooltip
                                const tooltipText = tooltips[0].textContent;
                                infoDiv.innerHTML = `<h3>Team Info</h3>${tooltipText}`;
                                infoDiv.style.display = 'block';
                                
                                // Hide after 3 seconds
                                setTimeout(function() {
                                    infoDiv.style.display = 'none';
                                }, 3000);
                            } else {
                                // If tooltip not found, show a message
                                infoDiv.innerHTML = `<h3>Team Selected</h3>
                                                    <p>Hover over point to see details</p>`;
                                infoDiv.style.display = 'block';
                                
                                // Hide after 3 seconds
                                setTimeout(function() {
                                    infoDiv.style.display = 'none';
                                }, 3000);
                            }
                        }
                    }, 100);
                }, { passive: false });
            });
        }, 1000); // Wait 1 second for Bokeh to initialize
    }
});