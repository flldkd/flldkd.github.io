// ============================================
// Homepage effects: typewriter, theme, scroll
// ============================================

// Typewriter effect
class TypeWriter {
    constructor(element, texts, options = {}) {
        this.element = element;
        this.texts = texts;
        this.textIndex = 0;
        this.charIndex = 0;
        this.isDeleting = false;
        this.speed = options.speed || 100;
        this.deleteSpeed = options.deleteSpeed || 50;
        this.pauseTime = options.pauseTime || 2000;
        
        this.type();
    }
    
    type() {
        const currentText = this.texts[this.textIndex];
        
        if (this.isDeleting) {
            this.element.textContent = currentText.substring(0, this.charIndex - 1);
            this.charIndex--;
            var typeSpeed = this.deleteSpeed;
        } else {
            this.element.textContent = currentText.substring(0, this.charIndex + 1);
            this.charIndex++;
            var typeSpeed = this.speed;
        }
        
        if (!this.isDeleting && this.charIndex === currentText.length) {
            typeSpeed = this.pauseTime;
            this.isDeleting = true;
        } else if (this.isDeleting && this.charIndex === 0) {
            this.isDeleting = false;
            this.textIndex = (this.textIndex + 1) % this.texts.length;
            typeSpeed = 500;
        }
        
        setTimeout(() => this.type(), typeSpeed);
    }
}

// Matrix rain (legacy, unused)
class MatrixRain {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.resize();
        
        this.matrix = "ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789@#$%^&*()*&^%+-/~{[|`]}";
        this.matrixArray = this.matrix.split("");
        
        this.fontSize = 14;
        this.columns = Math.floor(this.canvas.width / this.fontSize);
        this.drops = [];
        
        for (let x = 0; x < this.columns; x++) {
            this.drops[x] = Math.random() * -100;
        }
        
        this.animate();
        
        window.addEventListener('resize', () => this.resize());
    }
    
    resize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
        this.columns = Math.floor(this.canvas.width / this.fontSize);
    }
    
    draw() {
        // 淡入效果
        this.ctx.fillStyle = 'rgba(10, 10, 10, 0.05)';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // 设置字体和颜色
        this.ctx.fillStyle = '#00ff41';
        this.ctx.font = this.fontSize + 'px monospace';
        
        // 绘制字符
        for (let i = 0; i < this.drops.length; i++) {
            const text = this.matrixArray[Math.floor(Math.random() * this.matrixArray.length)];
            const x = i * this.fontSize;
            const y = this.drops[i] * this.fontSize;
            
            // 渐变效果
            const opacity = Math.min(1, (this.canvas.height - y) / 200);
            this.ctx.fillStyle = `rgba(0, 255, 65, ${opacity})`;
            
            this.ctx.fillText(text, x, y);
            
            // 重置drop
            if (y > this.canvas.height && Math.random() > 0.975) {
                this.drops[i] = 0;
            }
            
            this.drops[i]++;
        }
    }
    
    animate() {
        this.draw();
        requestAnimationFrame(() => this.animate());
    }
}

// 鼠标跟随效果
class CursorTrail {
    constructor() {
        this.cursor = document.querySelector('.cursor-trail');
        this.x = 0;
        this.y = 0;
        this.targetX = 0;
        this.targetY = 0;
        
        document.addEventListener('mousemove', (e) => {
            this.targetX = e.clientX;
            this.targetY = e.clientY;
        });
        
        this.animate();
    }
    
    animate() {
        this.x += (this.targetX - this.x) * 0.1;
        this.y += (this.targetY - this.y) * 0.1;
        
        this.cursor.style.left = this.x - 10 + 'px';
        this.cursor.style.top = this.y - 10 + 'px';
        this.cursor.style.opacity = '1';
        
        requestAnimationFrame(() => this.animate());
    }
}

// 系统时间更新
function updateSystemTime() {
    const timeElement = document.getElementById('system-time');
    if (timeElement) {
        const now = new Date();
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        const seconds = String(now.getSeconds()).padStart(2, '0');
        timeElement.textContent = `${hours}:${minutes}:${seconds}`;
    }
}

// 平滑滚动
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// 导航栏高亮
function initNavHighlight() {
    const sections = document.querySelectorAll('.block, .hero');
    const navLinks = document.querySelectorAll('.nav-link');
    
    window.addEventListener('scroll', () => {
        let current = '';
        
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            if (pageYOffset >= sectionTop - 200) {
                current = section.getAttribute('id');
            }
        });
        
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === '#' + current) {
                link.classList.add('active');
            }
        });
    });
}

// 区块进入动画
function initCardAnimations() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.05 });
    document.querySelectorAll('.block').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(12px)';
        el.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
        observer.observe(el);
    });
}

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    // Theme toggle (light / dark)
    const root = document.documentElement;
    const storedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    const initialTheme = storedTheme || (prefersDark ? 'dark' : 'light');
    root.setAttribute('data-theme', initialTheme);

    const themeToggle = document.querySelector('.theme-toggle');
    const updateToggleLabel = (theme) => {
        if (!themeToggle) return;
        themeToggle.textContent = theme === 'dark' ? 'Light' : 'Dark';
    };
    updateToggleLabel(initialTheme);

    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const current = root.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
            const next = current === 'dark' ? 'light' : 'dark';
            root.setAttribute('data-theme', next);
            localStorage.setItem('theme', next);
            updateToggleLabel(next);
        });
    }

    // Typewriter
    const typewriterElement = document.getElementById('typewriter');
    if (typewriterElement) {
        new TypeWriter(typewriterElement, [
            'Researcher · Developer · Explorer',
            'Student · Researcher · Innovator',
            'Explore the Unknown · Create the Future',
            'Hacker · Researcher · Creator'
        ], {
            speed: 100,
            deleteSpeed: 50,
            pauseTime: 2000
        });
    }
    
    // Smooth scroll
    initSmoothScroll();
    
    // Nav highlight on scroll
    initNavHighlight();
    
    // Block fade-in on scroll
    initCardAnimations();
});