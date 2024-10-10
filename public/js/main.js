document.addEventListener('DOMContentLoaded', function () {

    // Get all the buttons with the class 'preset-button'
    const buttons = document.querySelectorAll('.preset-button');
    const lights = document.querySelectorAll('.lamp-icon');
    buttons.forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault();

            fetch('/apply', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ preset_id: this.value }),
            })
                .then(response => response.json())
                .then(data => {
                    console.log('Response:', data);
                    if (data.success) {
                        console.log('Preset applied successfully:', data.message);
                        M.toast({ html: data.message, classes: 'green' });
                        // Loop through the data.lamp_data object and update the lamp icons
                        for (let lamp in data.lamp_data) {
                            updateLampIcon(data.lamp_data[lamp]);
                        }
                    } else {
                        console.error('Error applying preset:', data.message);
                        M.toast({ html: 'Error: ' + data.message, classes: 'red' });
                    }
                    // Unfocus the button after applying the preset
                    this.blur();
                })
                .catch(error => {
                    console.error('Error:', error);
                    M.toast({ html: 'An error occurred', classes: 'red' });
                });
        });
    });

    // Function to update lamp icon based on the data. 
    // Input data consists of a rgb color represent as a string "xxx,xxx,xxx" and a brightness level value.
    // The lamp icons have id's set as 'lamp-1', 'lamp-2', 'lamp-3', 'lamp-4' and the data should only be applied to a matching id.
    function updateLampIcon(data) {
        const lampIcon = document.getElementById('lamp-' + data.id);
        if (lampIcon) {
            lampIcon.style.color = 'rgb(' + data.rgb + ')';
            lampIcon.style.opacity = data.brightness;
        }
    }

    // Get the button to turn off all the lights by id 'nav-turn-off'
    const turnOffButton = document.getElementById('nav-turn-off');
    turnOffButton.addEventListener('click', function (e) {
        e.preventDefault()

        fetch('/turn-off', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({}),
        })
            .then(response => response.json())
            .then(data => {
                console.log('Response:', data);
                if (data.success) {
                    console.log('Lights turned off succesfully', data.message);
                    M.toast({ html: data.message, classes: 'green' });
                    // We need to construct a data object to update the lamp icons, based on the amount of lamp-icons we have.
                    const lampData = {};
                    for (let i = 1; i <= lights.length; i++) {
                        lampData[i] = { id: i, rgb: '0,0,0', brightness: 0 };
                    }
                    // Loop through the lampData object and update the lamp icons
                    for (let lamp in lampData) {
                        updateLampIcon(lampData[lamp]);
                    }
                } else {
                    console.error('Error applying preset:', data.message);
                    M.toast({ html: 'Error: ' + data.message, classes: 'red' });
                }
            })
            .catch(error => {
                console.error('Error:', error);
                M.toast({ html: 'An error occurred', classes: 'red' });
            });
    });

    // Update the presets with the button with the id 'nav-update-presets'
    const updatePresetsButton = document.getElementById('nav-update-presets');
    updatePresetsButton.addEventListener('click', function (e) {
        e.preventDefault()

        // Add a full page loader while updating the presets
        document.getElementById('loader').style.display = 'flex';

        // Do a fetch post request to the 'update-presets' endpoint and show a toast message based on the response
        fetch('/update-presets', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({}),
        })
            .then(response => response.json())
            .then(data => {
                console.log('Response:', data)
                if (data.success) {
                    console.log('Presets updated successfully', data.message);
                    M.toast({ html: data.message, classes: 'green' });
                    // Reload the page after updating the presets
                    location.reload();
                }
                else {
                    console.error('Error updating presets:', data.message);
                    document.getElementById('loader').style.display = 'none';
                    M.toast({ html: 'Error: ' + data.message, classes: 'red' });
                }
            })
            .catch(error => {
                console.error('Error:', error);
                document.getElementById('loader').style.display = 'none';
                M.toast({ html: 'An error occurred', classes: 'red' });
            });
    });
});

if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/service-worker.js')
            .then(registration => {
                console.log('ServiceWorker registration successful with scope: ', registration.scope);
            })
            .catch(error => {
                console.log('ServiceWorker registration failed:', error);
            });
    });
}