// 1. 初始化与配置
const SPREAD_CONFIG = {
    'single': { name: '单牌指引', count: 1, positions: ['当前指引'] },
    'three': { name: '三牌阵', count: 3, positions: ['过去', '现在', '未来'] },
    'celtic': { 
        name: '凯尔特十字', 
        count: 10, 
        positions: [
            '① 现状', '② 挑战', '③ 意识', '④ 潜意识', 
            '⑤ 过去', '⑥ 未来', '⑦ 自我', '⑧ 环境', 
            '⑨ 希望/恐惧', '⑩ 最终结果'
        ] 
    }
};

let currentSpread = 'single';
let selectedCardsData = [];
let currentSessionId = null;
let maxPicks = 1;

// DOM 元素
const setupScreen = document.getElementById('setup-screen');
const questionSection = document.getElementById('question-section');
const questionArea = document.getElementById('question-area');
const userQuestionInput = document.getElementById('user-question');
const shuffleBtn = document.getElementById('shuffle-btn');
const cardPickerArea = document.getElementById('card-picker-area');
const interactiveDeck = document.getElementById('interactive-deck');
const pickedShelf = document.getElementById('picked-shelf');
const pickGuide = document.getElementById('pick-guide');
const pickCountHint = document.getElementById('pick-count-hint');

const resultScreen = document.getElementById('result-screen');
const cardsDisplayContainer = document.getElementById('cards-display-container');
const interpretationBox = document.getElementById('interpretation-box');
const resultQuestionDisplay = document.getElementById('result-question-display');
const interpretationText = document.getElementById('interpretation-text');
const loadingSpinner = document.getElementById('loading-spinner');
const resetBtn = document.getElementById('reset-btn');
const savePosterBtn = document.getElementById('save-poster-btn');
const posterOverlay = document.getElementById('poster-overlay');
const posterPreviewContainer = document.getElementById('poster-preview-container');
const closePosterBtn = document.getElementById('close-poster-btn');

// 2. 牌阵选择逻辑
document.querySelectorAll('.spread-feature-card').forEach(card => {
    card.addEventListener('click', () => {
        currentSpread = card.dataset.spread;
        maxPicks = SPREAD_CONFIG[currentSpread].count;
        
        // UI 反馈
        document.querySelectorAll('.spread-feature-card').forEach(c => c.style.borderColor = 'var(--accent-gold-dim)');
        card.style.borderColor = 'var(--accent-gold)';
        
        // 显示问题输入区
        questionArea.style.display = 'block';
        questionArea.scrollIntoView({ behavior: 'smooth' });
    });
});

// 3. 开始洗牌
shuffleBtn.addEventListener('click', async () => {
    const question = userQuestionInput.value.trim();
    if (!question) {
        alert("请先写下您的困惑...");
        return;
    }

    shuffleBtn.disabled = true;
    shuffleBtn.textContent = "正在连接命运...";

    try {
        const res = await fetch('/api/tarot/shuffle', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question: question, spread: currentSpread })
        });
        const data = await res.json();
        currentSessionId = data.session_id;

        // 进入选牌阶段
        questionArea.style.display = 'none';
        if (document.querySelector('.hero-section')) document.querySelector('.hero-section').style.display = 'none';
        if (document.querySelector('.spread-gallery')) document.querySelector('.spread-gallery').style.display = 'none';
        
        cardPickerArea.style.display = 'block';
        cardPickerArea.scrollIntoView({ behavior: 'smooth' });
        
        pickCountHint.textContent = maxPicks;
        pickGuide.textContent = `正在选择：第 1 张牌 — ${SPREAD_CONFIG[currentSpread].positions[0]}`;
        
        generateInteractiveDeck(78);
    } catch (e) {
        alert("服务器连接失败，请重试");
        shuffleBtn.disabled = false;
        shuffleBtn.textContent = "✦ 开始洗牌 ✦";
    }
});

function generateInteractiveDeck(total) {
    interactiveDeck.innerHTML = '';
    const isMobile = window.innerWidth < 768;
    const spacing = isMobile ? 4 : 10;
    const angleStep = isMobile ? 0.8 : 1.5;
    const cardWidth = isMobile ? 50 : 70;

    for (let i = 0; i < total; i++) {
        const card = document.createElement('div');
        card.className = 'deck-card';
        // 扇形分布
        const angle = (i - total / 2) * angleStep;
        const translateX = (i - total / 2) * spacing;
        card.style.transform = `translateX(${translateX}px) rotate(${angle}deg)`;
        card.style.zIndex = i;
        card.addEventListener('click', () => pickCard(card, i));
        interactiveDeck.appendChild(card);
    }
}

async function pickCard(cardElement, index) {
    if (cardElement.classList.contains('picked') || selectedCardsData.length >= maxPicks) return;
    cardElement.classList.add('picked');

    try {
        const res = await fetch(`/api/tarot/reveal/${currentSessionId}/${index}`);
        const cardDetail = await res.json();
        selectedCardsData.push(cardDetail);

        // 飞入展示架并清除位移
        cardElement.style.transform = '';
        cardElement.style.left = '';
        cardElement.style.top = '';
        cardElement.classList.add('picked-to-shelf');
        cardElement.classList.add('revealed');
        cardElement.style.backgroundImage = `url('assets/cards/${cardDetail.name}.webp')`;
        
        if (cardDetail.status === '逆位') {
            cardElement.classList.add('reversed');
        }

        pickedShelf.appendChild(cardElement);

        const remaining = maxPicks - selectedCardsData.length;
        if (remaining === 0) {
            pickGuide.textContent = "✦ 选牌完成，即将解读 ✦";
            setTimeout(startInterpretation, 1000);
        } else {
            pickCountHint.textContent = remaining;
            const nextPos = SPREAD_CONFIG[currentSpread].positions[selectedCardsData.length];
            pickGuide.textContent = `正在选择：第 ${selectedCardsData.length + 1} 张牌 — ${nextPos}`;
        }
    } catch (e) {
        console.error(e);
    }
}

async function startInterpretation() {
    // 隐藏选牌区，进入结果页
    setupScreen.style.display = 'none';
    resultScreen.style.display = 'block';
    loadingSpinner.classList.add('active');

    // 展示用户问题
    resultQuestionDisplay.textContent = `「 ${userQuestionInput.value.trim()} 」`;

    displayCards(selectedCardsData, currentSpread);

    try {
        const res = await fetch('/api/interpret', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                cards: selectedCardsData, 
                spread_type: currentSpread,
                user_context: userQuestionInput.value.trim()
            })
        });
        const interpretData = await res.json();
        
        loadingSpinner.classList.remove('active');
        interpretationBox.classList.add('active');
        typeWriter(interpretData.interpretation, interpretationText);
    } catch (e) {
        interpretationText.innerHTML = "时空缝隙扰动，解读失败，请重试。";
    }
}

function displayCards(cards, spreadType) {
    cardsDisplayContainer.innerHTML = '';
    const config = SPREAD_CONFIG[spreadType];
    
    if (spreadType === 'celtic') {
        cardsDisplayContainer.className = 'celtic-layout';
    } else {
        cardsDisplayContainer.className = 'cards-row';
    }

    cards.forEach((card, index) => {
        const posName = config.positions[index];
        const cardWrapper = document.createElement('div');
        cardWrapper.className = 'selected-card-container';
        if (spreadType === 'celtic') cardWrapper.classList.add(`celtic-pos-${index+1}`);

        const cardDiv = document.createElement('div');
        cardDiv.className = 'card-display';
        if (card.status === '逆位') cardDiv.classList.add('reversed');
        if (spreadType === 'celtic' && index === 1) cardDiv.classList.add('card-crossing');
        
        cardDiv.style.backgroundImage = `url('assets/cards/${card.name}.webp')`;

        cardWrapper.innerHTML = `
            <p class="card-pos-label">${posName}</p>
            ${cardDiv.outerHTML}
            <h4 class="card-name-label">${card.name}</h4>
            <p class="card-status-label">(${card.status})</p>
        `;
        cardsDisplayContainer.appendChild(cardWrapper);
    });
}

function typeWriter(text, element) {
    // 1. 数据清洗：去除 ** 符号
    const cleanText = text.replace(/\*\*/g, '');
    
    element.innerHTML = '';
    let i = 0;
    const speed = 25; // 稍微调快一点，体验更好
    
    function type() {
        if (i < cleanText.length) {
            const char = cleanText.charAt(i);
            
            // 2. 智能换行：遇到 \n 转换为 <br>
            if (char === '\n') {
                element.innerHTML += '<br>';
            } else {
                element.innerHTML += char;
            }
            
            i++;
            // 滚动条自动跟随（可选，保证长文本能看到正在输入的行）
            if (i % 5 === 0) {
                element.scrollTop = element.scrollHeight;
            }
            setTimeout(type, speed);
        }
    }
    type();
}

resetBtn.addEventListener('click', () => {
    location.reload();
});

// ========== 海报生成逻辑 ==========
savePosterBtn.addEventListener('click', async () => {
    const originalText = savePosterBtn.textContent;
    savePosterBtn.textContent = '正在编织命运海报...';
    savePosterBtn.disabled = true;

    try {
        // 创建一个临时容器用于生成海报，确保样式精美
        const posterContent = document.createElement('div');
        posterContent.style.width = '600px';
        posterContent.style.padding = '40px';
        posterContent.style.background = 'linear-gradient(135deg, #05050a 0%, #0a0a1a 100%)';
        posterContent.style.color = '#e0e0e0';
        posterContent.style.fontFamily = "'Noto Serif SC', serif";
        posterContent.style.position = 'fixed';
        posterContent.style.top = '-9999px';
        posterContent.style.left = '-9999px';
        posterContent.style.border = '2px solid #d4a957';
        
        // 头部
        const header = document.createElement('div');
        header.innerHTML = `
            <h2 style="color: #a855f7; text-align: center; font-family: 'Cinzel', serif; letter-spacing: 5px; margin-bottom: 5px; text-shadow: 0 0 10px rgba(168, 85, 247, 0.5);">MYSTIC TAROT</h2>
            <p style="color: #d946ef; text-align: center; font-size: 12px; letter-spacing: 3px; margin-bottom: 30px; text-transform: uppercase;">神秘塔罗 · AI 命运启示</p>
            <div style="border-bottom: 1px solid rgba(168, 85, 247, 0.3); margin-bottom: 30px;"></div>
        `;
        posterContent.appendChild(header);

        // 强制执行隐私模式逻辑
        const displayQuestion = "「 命运的启示 」";
        const questionBox = document.createElement('div');
        questionBox.innerHTML = `
            <p style="color: #94a3b8; font-size: 14px; margin-bottom: 10px;">探索主题：</p>
            <p style="font-size: 18px; color: #fff; margin-bottom: 30px; line-height: 1.6; font-weight: 500;">${displayQuestion}</p>
        `;
        posterContent.appendChild(questionBox);

        // 牌阵展示
        const cardsDiv = document.createElement('div');
        cardsDiv.style.display = 'flex';
        cardsDiv.style.justifyContent = 'center';
        cardsDiv.style.gap = '20px';
        cardsDiv.style.marginBottom = '40px';
        cardsDiv.style.flexWrap = 'wrap';

        selectedCardsData.forEach(card => {
            const cWrap = document.createElement('div');
            cWrap.style.textAlign = 'center';
            cWrap.innerHTML = `
                <img src="assets/cards/${card.name}.webp" style="width: 100px; border: 1.5px solid #a855f7; box-shadow: 0 8px 20px rgba(0,0,0,0.8); border-radius: 8px; ${card.status === '逆位' ? 'transform: rotate(180deg);' : ''}">
                <p style="color: #a855f7; margin-top: 12px; font-size: 15px; font-weight: 600;">${card.name}</p>
                <p style="color: #94a3b8; font-size: 12px;">(${card.status})</p>
            `;
            cardsDiv.appendChild(cWrap);
        });
        posterContent.appendChild(cardsDiv);

        // 解读摘要 (强制脱敏处理)
        const fullInterpretation = interpretationText.innerText;
        let displayInterpretation = fullInterpretation.split(/[。！\n]/)[0] + "。";
        displayInterpretation += "\n\n( 详细内容已隐藏，唯有心诚者自知 )";

        const interpretation = document.createElement('div');
        interpretation.innerHTML = `
            <div style="border-left: 3px solid #a855f7; padding-left: 20px; margin-bottom: 30px;">
                <h4 style="color: #a855f7; margin-bottom: 15px; font-size: 16px;">✦ AI 灵性指引摘要</h4>
                <p style="font-size: 14px; line-height: 1.8; color: #cbd5e1; text-align: justify;">
                    ${displayInterpretation}
                </p>
            </div>
        `;
        posterContent.appendChild(interpretation);

        // 页脚
        const footer = document.createElement('div');
        footer.innerHTML = `
            <div style="border-top: 1px solid rgba(168, 85, 247, 0.2); padding-top: 20px; display: flex; justify-content: space-between; align-items: center;">
                <p style="color: #64748b; font-size: 11px;">生成日期：${new Date().toLocaleDateString()}</p>
                <p style="color: #a855f7; font-size: 13px; letter-spacing: 1px; font-weight: 600;">由 知了 AI 提供指引</p>
            </div>
        `;
        posterContent.appendChild(footer);

        document.body.appendChild(posterContent);

        // 使用 html2canvas 生成图片
        const canvas = await html2canvas(posterContent, {
            useCORS: true,
            backgroundColor: '#05050a',
            scale: 2 // 提高清晰度
        });

        const imgData = canvas.toDataURL('image/png');
        posterPreviewContainer.innerHTML = `<img src="${imgData}" alt="Tarot Poster">`;
        posterOverlay.classList.add('active');

        // 移除临时 DOM
        document.body.removeChild(posterContent);
        
    } catch (e) {
        console.error(e);
        alert('海报生成失败，请稍后重试');
    } finally {
        savePosterBtn.textContent = originalText;
        savePosterBtn.disabled = false;
    }
});

closePosterBtn.addEventListener('click', () => {
    posterOverlay.classList.remove('active');
});

// ========== 用户认证逻辑 ==========
const authOverlay = document.getElementById('auth-overlay');
const showLoginBtn = document.getElementById('show-login-btn');
const userInfo = document.getElementById('user-info');
const userNickname = document.getElementById('user-nickname');
const authForm = document.getElementById('auth-form');
const nicknameField = document.getElementById('nickname-field');
const authSubmitBtn = document.getElementById('auth-submit-btn');
const authError = document.getElementById('auth-error');
let currentAuthMode = 'login'; // 'login' or 'register'

function showAuthModal() {
    authOverlay.style.display = 'flex';
}

function hideAuthModal() {
    authOverlay.style.display = 'none';
    authError.textContent = '';
}

function switchAuthTab(mode) {
    currentAuthMode = mode;
    document.getElementById('tab-login').classList.toggle('active', mode === 'login');
    document.getElementById('tab-register').classList.toggle('active', mode === 'register');
    
    nicknameField.style.display = mode === 'register' ? 'block' : 'none';
    authSubmitBtn.textContent = mode === 'login' ? '登录' : '注册';
    authError.textContent = '';
}

function getAuthHeader() {
    const token = localStorage.getItem('mystic_token');
    return token ? { 'Authorization': `Bearer ${token}` } : {};
}

function updateAuthUI(user) {
    if (user) {
        showLoginBtn.style.display = 'none';
        userInfo.style.display = 'flex';
        userNickname.textContent = user.nickname || user.username;
    } else {
        showLoginBtn.style.display = 'inline-block';
        userInfo.style.display = 'none';
        userNickname.textContent = '';
    }
}

async function handleAuthSubmit(e) {
    e.preventDefault();
    const username = document.getElementById('auth-username').value.trim();
    const password = document.getElementById('auth-password').value;
    const nickname = document.getElementById('auth-nickname').value.trim();
    
    if (username.length < 2) {
        authError.textContent = '用户名太短';
        return;
    }
    if (password.length < 6) {
        authError.textContent = '密码至少6位';
        return;
    }
    
    authSubmitBtn.disabled = true;
    authSubmitBtn.textContent = '请稍候...';
    authError.textContent = '';
    
    try {
        const endpoint = currentAuthMode === 'login' ? '/api/auth/login' : '/api/auth/register';
        const res = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password, nickname })
        });
        
        const data = await res.json();
        if (!res.ok) {
            throw new Error(data.detail || '请求失败');
        }
        
        if (currentAuthMode === 'login') {
            localStorage.setItem('mystic_token', data.token);
            updateAuthUI(data);
            hideAuthModal();
        } else {
            // 注册成功后自动切到登录
            switchAuthTab('login');
            authError.style.color = '#4ade80';
            authError.textContent = '注册成功，请登录';
            setTimeout(() => { authError.style.color = '#f87171'; authError.textContent = ''; }, 3000);
        }
    } catch (err) {
        authError.textContent = err.message;
    } finally {
        authSubmitBtn.disabled = false;
        authSubmitBtn.textContent = currentAuthMode === 'login' ? '登录' : '注册';
    }
}

async function handleLogout() {
    try {
        await fetch('/api/auth/logout', {
            method: 'POST',
            headers: getAuthHeader()
        });
    } catch (e) {
        console.error('Logout error:', e);
    }
    localStorage.removeItem('mystic_token');
    updateAuthUI(null);
}

// 页面加载时检查登录状态
async function checkLoginStatus() {
    const token = localStorage.getItem('mystic_token');
    if (!token) return;
    
    try {
        const res = await fetch('/api/auth/me', { headers: getAuthHeader() });
        if (res.ok) {
            const user = await res.json();
            updateAuthUI(user);
        } else {
            localStorage.removeItem('mystic_token');
        }
    } catch (e) {
        console.error('Check login status error:', e);
    }
}

// 替换掉原来的 generateInterpretation 中的 fetch 调用，带上 Auth header
const originalGenerateInterpretation = window.generateInterpretation || async function() {};

// 这里我们需要修改 generateInterpretation 函数里面的 fetch 请求
// 因为它是直接在代码中间定义的，我们在页面加载完后再去覆盖那个按钮的行为，或者直接在这里覆盖整个函数
window.generateInterpretation = async function() {
    interpretationContent.innerHTML = '<p class="loading-text">正在连接宇宙意志，为您解读...</p>';
    
    try {
        const res = await fetch('/api/interpret', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                ...getAuthHeader() // 加上 token，后端好记录是谁测的
            },
            body: JSON.stringify({
                cards: selectedCardsData,
                spread_type: currentSpread,
                user_context: userQuestionInput.value.trim()
            })
        });
        
        const data = await res.json();
        // 处理换行符，转换为 HTML 段落
        const formattedHtml = data.interpretation.split('\\n').map(p => p.trim() ? `<p>${p}</p>` : '').join('');
        interpretationContent.innerHTML = formattedHtml;
    } catch (e) {
        console.error(e);
        interpretationContent.innerHTML = '<p class="error-text">连接受阻，请稍后重试。</p>';
    }
}

// 初始化
document.addEventListener('DOMContentLoaded', checkLoginStatus);
