        // ========== GSAP REGISTER ==========
        if (typeof gsap !== 'undefined' && typeof ScrollTrigger !== 'undefined') {
            gsap.registerPlugin(ScrollTrigger);
        }

        // ========== CURSOR GLOW ==========
        const cursorGlow = document.getElementById('cursorGlow');
        let mouseX = 0, mouseY = 0, glowX = 0, glowY = 0;

        document.addEventListener('mousemove', (e) => {
            mouseX = e.clientX;
            mouseY = e.clientY;
        });

        function animateGlow() {
            glowX += (mouseX - glowX) * 0.1;
            glowY += (mouseY - glowY) * 0.1;
            cursorGlow.style.left = glowX + 'px';
            cursorGlow.style.top = glowY + 'px';
            requestAnimationFrame(animateGlow);
        }
        animateGlow();

        // ========== CARD TILT / MOUSE TRACKING ==========
        document.querySelectorAll('.demo-card, .persona-card').forEach(card => {
            card.addEventListener('mousemove', (e) => {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                const centerX = rect.width / 2;
                const centerY = rect.height / 2;
                const rotateX = (y - centerY) / 20;
                const rotateY = (centerX - x) / 20;

                card.style.setProperty('--mouse-x', x + 'px');
                card.style.setProperty('--mouse-y', y + 'px');

                if (card.classList.contains('demo-card')) {
                    card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
                }
            });

            card.addEventListener('mouseleave', () => {
                card.style.transform = '';
            });
        });

        // Track mouse on persona cards for radial gradient
        document.querySelectorAll('.persona-card').forEach(card => {
            card.addEventListener('mousemove', (e) => {
                const rect = card.getBoundingClientRect();
                card.style.setProperty('--mouse-x', (e.clientX - rect.left) + 'px');
                card.style.setProperty('--mouse-y', (e.clientY - rect.top) + 'px');
            });
        });

        // ========== NAV SCROLL ==========
        const nav = document.getElementById('nav');
        window.addEventListener('scroll', () => {
            nav.classList.toggle('scrolled', window.scrollY > 50);
        });

        // ========== MOBILE MENU ==========
        const mobileToggle = document.getElementById('mobileToggle');
        const navLinks = document.getElementById('navLinks');
        mobileToggle.addEventListener('click', () => {
            navLinks.classList.toggle('open');
        });

        navLinks.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => navLinks.classList.remove('open'));
        });

        // ========== SCROLL REVEAL ANIMATIONS ==========
        if (typeof gsap !== 'undefined') {
            document.querySelectorAll('.reveal').forEach((el, i) => {
                gsap.fromTo(el,
                    { opacity: 0, y: 40 },
                    {
                        opacity: 1,
                        y: 0,
                        duration: 0.8,
                        ease: 'power3.out',
                        scrollTrigger: {
                            trigger: el,
                            start: 'top 85%',
                            toggleActions: 'play none none none'
                        },
                        delay: (i % 3) * 0.1
                    }
                );
            });

            // ========== COUNTER ANIMATION ==========
            document.querySelectorAll('.stat-number').forEach(el => {
                const target = parseInt(el.getAttribute('data-count'));
                ScrollTrigger.create({
                    trigger: el,
                    start: 'top 85%',
                    onEnter: () => {
                        gsap.to({ val: 0 }, {
                            val: target,
                            duration: 2,
                            ease: 'power2.out',
                            onUpdate: function() {
                                el.textContent = Math.round(this.targets()[0].val) + '%';
                            }
                        });
                    },
                    once: true
                });
            });
        }

        // ========== INTERACTIVE CALCULATOR + CHART ==========
        const FISCAL_ANNUAL = 2400000; // $200k/mes * 12

        function formatCOP(val) {
            return '$' + val.toLocaleString('es-CO');
        }

        // Chart.js bar chart
        const costCtx = document.getElementById('costChart').getContext('2d');
        const costChart = new Chart(costCtx, {
            type: 'bar',
            data: {
                labels: ['Metodo Tradicional', 'FiscalAI'],
                datasets: [{
                    label: 'Costo Anual (COP)',
                    data: [11250000, FISCAL_ANNUAL],
                    backgroundColor: ['#ef4444', '#10b981'],
                    borderRadius: 8,
                    barPercentage: 0.55,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                animation: { duration: 600, easing: 'easeOutQuart' },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: function(ctx) { return formatCOP(ctx.parsed.y) + ' COP'; }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            color: '#64748b',
                            callback: function(v) { return '$' + (v / 1000000).toFixed(0) + 'M'; }
                        },
                        grid: { color: 'rgba(255,255,255,0.04)' }
                    },
                    x: {
                        ticks: { color: '#94a3b8', font: { weight: 600 } },
                        grid: { display: false }
                    }
                }
            }
        });

        const salaryRange = document.getElementById('salaryRange');
        const hoursRange = document.getElementById('hoursRange');

        function updateCalculator() {
            const salary = parseInt(salaryRange.value);
            const hours = parseInt(hoursRange.value);

            document.getElementById('salaryValue').textContent = formatCOP(salary) + ' COP';
            document.getElementById('hoursValue').textContent = hours + 'h';

            const hourlyRate = salary / 160;
            const annual = Math.round(hourlyRate * hours * 12);
            const savings = Math.max(0, annual - FISCAL_ANNUAL);
            const pct = annual > 0 ? Math.round((savings / annual) * 100) : 0;

            document.getElementById('annualCost').textContent = formatCOP(annual) + ' COP';
            document.getElementById('savingsAmount').textContent = formatCOP(savings) + ' COP';
            document.getElementById('savingsPercent').textContent = pct + '%';

            // Update chart
            costChart.data.datasets[0].data[0] = annual;
            costChart.update();
        }

        salaryRange.addEventListener('input', updateCalculator);
        hoursRange.addEventListener('input', updateCalculator);
        updateCalculator();

        // ========== COMPETITION BUBBLE CHART ==========
        const compCtx = document.getElementById('competitionChart').getContext('2d');
        new Chart(compCtx, {
            type: 'bubble',
            data: {
                datasets: [
                    {
                        label: 'Siigo',
                        data: [{ x: 70, y: 90, r: 18 }],
                        backgroundColor: 'rgba(239, 68, 68, 0.55)',
                        borderColor: '#ef4444',
                        borderWidth: 2,
                        hoverBackgroundColor: 'rgba(239, 68, 68, 0.8)'
                    },
                    {
                        label: 'Alegra',
                        data: [{ x: 55, y: 60, r: 14 }],
                        backgroundColor: 'rgba(59, 130, 246, 0.55)',
                        borderColor: '#3b82f6',
                        borderWidth: 2,
                        hoverBackgroundColor: 'rgba(59, 130, 246, 0.8)'
                    },
                    {
                        label: 'Treinta',
                        data: [{ x: 30, y: 25, r: 16 }],
                        backgroundColor: 'rgba(168, 85, 247, 0.55)',
                        borderColor: '#a855f7',
                        borderWidth: 2,
                        hoverBackgroundColor: 'rgba(168, 85, 247, 0.8)'
                    },
                    {
                        label: 'Numbi.ai',
                        data: [{ x: 65, y: 75, r: 10 }],
                        backgroundColor: 'rgba(251, 191, 36, 0.55)',
                        borderColor: '#f59e0b',
                        borderWidth: 2,
                        hoverBackgroundColor: 'rgba(251, 191, 36, 0.8)'
                    },
                    {
                        label: 'FiscalAI',
                        data: [{ x: 90, y: 15, r: 16 }],
                        backgroundColor: 'rgba(16, 185, 129, 0.65)',
                        borderColor: '#10b981',
                        borderWidth: 3,
                        hoverBackgroundColor: 'rgba(16, 185, 129, 0.9)'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#94a3b8',
                            usePointStyle: true,
                            pointStyle: 'circle',
                            padding: 20,
                            font: { size: 12, weight: 500 }
                        }
                    },
                    tooltip: {
                        backgroundColor: '#1e293b',
                        titleColor: '#f1f5f9',
                        bodyColor: '#94a3b8',
                        borderColor: 'rgba(255,255,255,0.1)',
                        borderWidth: 1,
                        padding: 12,
                        callbacks: {
                            label: function(ctx) {
                                return ctx.dataset.label +
                                    ' — Automatizacion: ' + ctx.parsed.x +
                                    '% | Costo: ' + ctx.parsed.y + '%';
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Nivel de Automatizacion →',
                            color: '#64748b',
                            font: { weight: 600, size: 12 }
                        },
                        min: 0, max: 100,
                        ticks: { color: '#475569', stepSize: 20 },
                        grid: { color: 'rgba(255,255,255,0.04)' }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Costo para el Cliente →',
                            color: '#64748b',
                            font: { weight: 600, size: 12 }
                        },
                        min: 0, max: 100,
                        ticks: { color: '#475569', stepSize: 20 },
                        grid: { color: 'rgba(255,255,255,0.04)' }
                    }
                }
            }
        });

        // ========== HERO ANIMATION SEQUENCE ==========
        if (typeof gsap !== 'undefined') {
            const heroTl = gsap.timeline({ delay: 0.2 });
            heroTl
                .fromTo('.hero-badge', { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.6 })
                .fromTo('.hero h1', { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.7 }, '-=0.3')
                .fromTo('.hero-desc', { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.6 }, '-=0.4')
                .fromTo('.hero-actions', { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.6 }, '-=0.3')
                .fromTo('.demo-card', { opacity: 0, y: 40, scale: 0.95 }, { opacity: 1, y: 0, scale: 1, duration: 0.8, ease: 'back.out(1.2)' }, '-=0.4')
                .fromTo('.demo-step', { opacity: 0, x: -20 }, { opacity: 1, x: 0, duration: 0.4, stagger: 0.15 }, '-=0.4');
        }

        // ========== DEMO STEP ANIMATION (CYCLING) ==========
        const demoSteps = [
            document.getElementById('demoStep1'),
            document.getElementById('demoStep2'),
            document.getElementById('demoStep3')
        ];
        let activeStep = 1;

        setInterval(() => {
            demoSteps.forEach(s => s.classList.remove('active'));
            activeStep = (activeStep + 1) % 3;
            demoSteps[activeStep].classList.add('active');
        }, 2500);

        // ========== LEAD CAPTURE FORM ==========
        (function() {
            const STORAGE_KEY = 'fiscalai_lead';
            const gate = document.getElementById('demoGateOverlay');
            const content = document.getElementById('demoLiveContent');
            const form = document.getElementById('leadForm');
            const errorEl = document.getElementById('leadFormError');
            const errorText = document.getElementById('leadFormErrorText');
            const successEl = document.getElementById('leadSuccess');
            const submitBtn = document.getElementById('leadSubmitBtn');

            // URL base del backend — en producción apunta a tu app de Fly.io
            var API_BASE = window.FISCALAI_API_BASE || 'https://fiscalai.fly.dev';

            // Check if user already submitted (localStorage como caché local)
            const existingLead = localStorage.getItem(STORAGE_KEY);
            if (existingLead) {
                unlockDemo(true);
            }

            function unlockDemo(instant) {
                if (instant) {
                    gate.classList.add('hidden');
                    content.style.display = '';
                } else {
                    // Show success message first
                    form.style.display = 'none';
                    successEl.classList.add('visible');

                    // Then hide gate and show demo after a brief delay
                    setTimeout(function() {
                        gate.classList.add('hidden');
                        content.style.display = '';
                        // Scroll to the demo content smoothly
                        content.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }, 2000);
                }
            }

            function validateEmail(email) {
                return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
            }

            function showError(msg) {
                errorText.textContent = msg;
                errorEl.classList.add('visible');
            }

            function clearError() {
                errorEl.classList.remove('visible');
            }

            function clearFieldErrors() {
                form.querySelectorAll('.error').forEach(function(el) {
                    el.classList.remove('error');
                });
            }

            form.addEventListener('submit', function(e) {
                e.preventDefault();
                clearError();
                clearFieldErrors();

                var name = document.getElementById('leadName').value.trim();
                var email = document.getElementById('leadEmail').value.trim();
                var phone = document.getElementById('leadPhone').value.trim();
                var company = document.getElementById('leadCompany').value.trim();
                var role = document.getElementById('leadRole').value;
                var volume = document.getElementById('leadVolume').value;

                // Validate required fields
                var hasError = false;

                if (!name) {
                    document.getElementById('leadName').classList.add('error');
                    hasError = true;
                }
                if (!email) {
                    document.getElementById('leadEmail').classList.add('error');
                    hasError = true;
                } else if (!validateEmail(email)) {
                    document.getElementById('leadEmail').classList.add('error');
                    showError('Por favor ingresa un correo electronico valido.');
                    return;
                }
                if (!phone) {
                    document.getElementById('leadPhone').classList.add('error');
                    hasError = true;
                }
                if (!company) {
                    document.getElementById('leadCompany').classList.add('error');
                    hasError = true;
                }

                if (hasError) {
                    showError('Por favor completa los campos obligatorios.');
                    return;
                }

                // Disable button while processing
                submitBtn.disabled = true;
                submitBtn.textContent = 'Procesando...';

                // Build lead data object
                var leadData = {
                    name: name,
                    email: email,
                    phone: phone,
                    company: company,
                    role: role || null,
                    volume: volume || null,
                    source: 'demo_gate'
                };

                // ── Enviar al backend ─────────────────────────────────────
                fetch(API_BASE + '/api/leads/demo', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(leadData)
                })
                .then(function(res) { return res.json(); })
                .then(function(data) {
                    if (data.ok) {
                        // Guardar en localStorage como caché (evita reenviar en recarga)
                        localStorage.setItem(STORAGE_KEY, JSON.stringify(leadData));
                        unlockDemo(false);
                    } else {
                        showError('Hubo un problema. Por favor intenta de nuevo.');
                        submitBtn.disabled = false;
                        submitBtn.textContent = 'Acceder a la Demo Gratis';
                    }
                })
                .catch(function(err) {
                    console.error('[FiscalAI] Error al enviar lead:', err);
                    // Fallback: si el backend no está disponible, igual desbloqueamos
                    localStorage.setItem(STORAGE_KEY, JSON.stringify(leadData));
                    unlockDemo(false);
                });
            });
        })();

        // ========== PRICING MODAL ==========
        (function() {
            var API_BASE = window.FISCALAI_API_BASE || 'https://fiscalai.fly.dev';
            var overlay = document.getElementById('pricingModal');
            var closeBtn = document.getElementById('pricingModalClose');
            var planLabel = document.getElementById('pricingModalPlan');
            var form = document.getElementById('pricingContactForm');
            var errorEl = document.getElementById('pcError');
            var errorText = document.getElementById('pcErrorText');
            var successEl = document.getElementById('pcSuccess');
            var submitBtn = document.getElementById('pcSubmitBtn');
            var currentPlan = '';

            document.querySelectorAll('.btn-pricing').forEach(function(btn) {
                btn.addEventListener('click', function() {
                    var card = btn.closest('.pricing-card');
                    currentPlan = card.querySelector('h3').textContent.trim();
                    planLabel.textContent = currentPlan;
                    form.reset();
                    form.style.display = '';
                    successEl.classList.remove('visible');
                    errorEl.classList.remove('visible');
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 12h14M12 5l7 7-7 7"/></svg> Enviar mensaje';
                    overlay.classList.add('open');
                    document.body.style.overflow = 'hidden';
                });
            });

            function closeModal() {
                overlay.classList.remove('open');
                document.body.style.overflow = '';
            }

            closeBtn.addEventListener('click', closeModal);
            overlay.addEventListener('click', function(e) {
                if (e.target === overlay) closeModal();
            });
            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape') closeModal();
            });

            form.addEventListener('submit', function(e) {
                e.preventDefault();
                errorEl.classList.remove('visible');

                var name = document.getElementById('pcName').value.trim();
                var email = document.getElementById('pcEmail').value.trim();
                var message = document.getElementById('pcMessage').value.trim();

                if (!name || !email || !message) {
                    errorText.textContent = 'Por favor completa todos los campos.';
                    errorEl.classList.add('visible');
                    return;
                }
                if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
                    errorText.textContent = 'Ingresa un correo valido.';
                    errorEl.classList.add('visible');
                    return;
                }

                submitBtn.disabled = true;
                submitBtn.textContent = 'Enviando...';

                fetch(API_BASE + '/api/leads/pricing', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name: name, email: email, plan: currentPlan, message: message, source: 'pricing_modal' })
                })
                .then(function(res) { return res.json(); })
                .then(function(data) {
                    if (data.ok) {
                        form.style.display = 'none';
                        successEl.classList.add('visible');
                        setTimeout(closeModal, 2500);
                    } else {
                        errorText.textContent = 'Hubo un problema. Intenta de nuevo.';
                        errorEl.classList.add('visible');
                        submitBtn.disabled = false;
                        submitBtn.textContent = 'Enviar mensaje';
                    }
                })
                .catch(function() {
                    form.style.display = 'none';
                    successEl.classList.add('visible');
                    setTimeout(closeModal, 2500);
                });
            });
        })();
