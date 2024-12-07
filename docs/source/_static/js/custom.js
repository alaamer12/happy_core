// Add smooth scroll for footer links
document.addEventListener('DOMContentLoaded', function() {
    const footerLinks = document.querySelectorAll('.footer-links a');
    
    footerLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href.startsWith('#')) {
                e.preventDefault();
                document.querySelector(href).scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Add hover effect for package status dots
    const packageLinks = document.querySelectorAll('.footer-package');
    packageLinks.forEach(link => {
        const dot = link.querySelector('.status-dot');
        if (dot) {
            link.addEventListener('mouseenter', () => {
                dot.style.transform = 'scale(1.2)';
            });
            link.addEventListener('mouseleave', () => {
                dot.style.transform = 'scale(1)';
            });
        }
    });
});