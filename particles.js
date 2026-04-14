// ============================================
// 粒子系统 - 赛博朋克风格
// ============================================

class ParticleSystem {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.resize();
        
        this.particles = [];
        this.particleCount = 80;
        this.mouse = { x: 0, y: 0 };
        this.connectionDistance = 150;
        
        // 创建粒子
        this.initParticles();
        
        // 鼠标追踪
        document.addEventListener('mousemove', (e) => {
            this.mouse.x = e.clientX;
            this.mouse.y = e.clientY;
        });
        
        // 动画循环
        this.animate();
        
        window.addEventListener('resize', () => this.resize());
    }
    
    resize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
        if (this.particles.length === 0) {
            this.initParticles();
        } else {
            // 调整现有粒子的位置
            this.particles.forEach(particle => {
                if (particle.x > this.canvas.width) particle.x = this.canvas.width;
                if (particle.y > this.canvas.height) particle.y = this.canvas.height;
            });
        }
    }
    
    initParticles() {
        this.particles = [];
        for (let i = 0; i < this.particleCount; i++) {
            this.particles.push(new Particle(
                Math.random() * this.canvas.width,
                Math.random() * this.canvas.height,
                this.canvas.width,
                this.canvas.height
            ));
        }
    }
    
    drawConnections() {
        for (let i = 0; i < this.particles.length; i++) {
            for (let j = i + 1; j < this.particles.length; j++) {
                const dx = this.particles[i].x - this.particles[j].x;
                const dy = this.particles[i].y - this.particles[j].y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                if (distance < this.connectionDistance) {
                    const opacity = (1 - distance / this.connectionDistance) * 0.3;
                    this.ctx.strokeStyle = `rgba(0, 255, 255, ${opacity})`;
                    this.ctx.lineWidth = 1;
                    this.ctx.beginPath();
                    this.ctx.moveTo(this.particles[i].x, this.particles[i].y);
                    this.ctx.lineTo(this.particles[j].x, this.particles[j].y);
                    this.ctx.stroke();
                }
            }
        }
        
        // 鼠标到粒子的连接
        this.particles.forEach(particle => {
            const dx = this.mouse.x - particle.x;
            const dy = this.mouse.y - particle.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            
            if (distance < this.connectionDistance * 1.5) {
                const opacity = (1 - distance / (this.connectionDistance * 1.5)) * 0.5;
                this.ctx.strokeStyle = `rgba(255, 0, 255, ${opacity})`;
                this.ctx.lineWidth = 2;
                this.ctx.beginPath();
                this.ctx.moveTo(this.mouse.x, this.mouse.y);
                this.ctx.lineTo(particle.x, particle.y);
                this.ctx.stroke();
            }
        });
    }
    
    draw() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // 绘制连接线
        this.drawConnections();
        
        // 更新和绘制粒子
        this.particles.forEach(particle => {
            particle.update();
            particle.draw(this.ctx);
        });
    }
    
    animate() {
        this.draw();
        requestAnimationFrame(() => this.animate());
    }
}

// 粒子类
class Particle {
    constructor(x, y, maxWidth, maxHeight) {
        this.x = x;
        this.y = y;
        this.maxWidth = maxWidth;
        this.maxHeight = maxHeight;
        this.vx = (Math.random() - 0.5) * 0.5;
        this.vy = (Math.random() - 0.5) * 0.5;
        this.size = Math.random() * 2 + 1;
        this.color = this.getRandomColor();
        this.opacity = Math.random() * 0.5 + 0.5;
        this.glowSize = this.size * 3;
    }
    
    getRandomColor() {
        const colors = [
            'rgba(0, 255, 255, ',    // cyan
            'rgba(0, 255, 65, ',     // green
            'rgba(255, 0, 255, ',    // purple
            'rgba(255, 20, 147, ',   // pink
            'rgba(0, 128, 255, '     // blue
        ];
        return colors[Math.floor(Math.random() * colors.length)];
    }
    
    update() {
        this.x += this.vx;
        this.y += this.vy;
        
        // 边界反弹
        if (this.x < 0 || this.x > this.maxWidth) {
            this.vx *= -1;
        }
        if (this.y < 0 || this.y > this.maxHeight) {
            this.vy *= -1;
        }
        
        // 确保在边界内
        this.x = Math.max(0, Math.min(this.maxWidth, this.x));
        this.y = Math.max(0, Math.min(this.maxHeight, this.y));
        
        // 轻微的随机运动
        this.vx += (Math.random() - 0.5) * 0.02;
        this.vy += (Math.random() - 0.5) * 0.02;
        
        // 限制速度
        const maxSpeed = 1;
        const speed = Math.sqrt(this.vx * this.vx + this.vy * this.vy);
        if (speed > maxSpeed) {
            this.vx = (this.vx / speed) * maxSpeed;
            this.vy = (this.vy / speed) * maxSpeed;
        }
        
        // 脉动效果
        this.opacity = 0.5 + Math.sin(Date.now() * 0.003 + this.x * 0.01) * 0.3;
    }
    
    draw(ctx) {
        // 绘制发光效果
        const gradient = ctx.createRadialGradient(
            this.x, this.y, 0,
            this.x, this.y, this.glowSize
        );
        gradient.addColorStop(0, this.color + this.opacity + ')');
        gradient.addColorStop(0.5, this.color + this.opacity * 0.5 + ')');
        gradient.addColorStop(1, this.color + '0)');
        
        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.glowSize, 0, Math.PI * 2);
        ctx.fill();
        
        // 绘制核心粒子
        ctx.fillStyle = this.color + '1)';
        ctx.shadowBlur = 10;
        ctx.shadowColor = this.color.replace('rgba(', '#').replace(', ', '').split(',')[0] + ')';
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fill();
        ctx.shadowBlur = 0;
    }
}

// 初始化粒子系统
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('particles-canvas')) {
        new ParticleSystem('particles-canvas');
    }
});

