// Check if service worker is supported
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/pwa/sw.js')
            .then(registration => {
                console.log('Service Worker registered successfully:', registration);
            })
            .catch(error => {
                console.log('Service Worker registration failed:', error);
            });
    });
}

// PWA installation handling
let deferredPrompt;
const installButton = document.createElement('button');
installButton.style.display = 'none';
installButton.classList.add('btn', 'btn-primary', 'install-button');
installButton.textContent = 'Instalar App';

// Add install button to navbar
document.addEventListener('DOMContentLoaded', () => {
    const navbar = document.querySelector('.navbar-nav');
    if (navbar) {
        const li = document.createElement('li');
        li.classList.add('nav-item');
        li.appendChild(installButton);
        navbar.appendChild(li);
    }
});

window.addEventListener('beforeinstallprompt', (e) => {
    // Prevent Chrome 67 and earlier from automatically showing the prompt
    e.preventDefault();
    // Stash the event so it can be triggered later
    deferredPrompt = e;
    // Show the install button
    installButton.style.display = 'block';
});

installButton.addEventListener('click', async () => {
    if (deferredPrompt) {
        // Show the install prompt
        deferredPrompt.prompt();
        // Wait for the user to respond to the prompt
        const { outcome } = await deferredPrompt.userChoice;
        console.log(`User response to the install prompt: ${outcome}`);
        // Clear the deferredPrompt variable
        deferredPrompt = null;
        // Hide the install button
        installButton.style.display = 'none';
    }
});

// Detecta se o app já está instalado
window.addEventListener('appinstalled', (evt) => {
    console.log('HangoutStreak foi instalado!');
}); 