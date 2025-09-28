/**
 * 图片转换服务 - 认证模块
 */

class AuthService {
    constructor() {
        this.baseURL = window.location.origin;
        this.token = localStorage.getItem('auth_token');
        this.user = JSON.parse(localStorage.getItem('user_info') || 'null');
    }

    /**
     * 获取客户端IP地址
     */
    async getClientIP() {
        try {
            const response = await fetch('https://api.ipify.org?format=json');
            const data = await response.json();
            return data.ip;
        } catch (error) {
            console.error('获取IP失败:', error);
            return '8.8.8.8'; // 默认IP
        }
    }

    /**
     * 获取智能登录推荐
     */
    async getSmartLogin() {
        try {
            const clientIP = await this.getClientIP();
            const hostID = 'web-' + Date.now();
            
            const response = await fetch(`${this.baseURL}/api/auth/smart/login?client_ip=${clientIP}&host_id=${hostID}`);
            const data = await response.json();
            
            return data;
        } catch (error) {
            console.error('获取登录推荐失败:', error);
            throw error;
        }
    }

    /**
     * 发起Auth0登录
     */
    async auth0Login() {
        try {
            const response = await fetch(`${this.baseURL}/api/auth/auth0/login`);
            const data = await response.json();
            
            // 跳转到Auth0登录页面
            window.location.href = data.auth_url;
        } catch (error) {
            console.error('Auth0登录失败:', error);
            throw error;
        }
    }

    /**
     * 发起Google直接登录
     */
    async googleLogin() {
        try {
            const response = await fetch(`${this.baseURL}/api/auth/google/login`);
            const data = await response.json();
            
            // 跳转到Google登录页面
            window.location.href = data.auth_url;
        } catch (error) {
            console.error('Google登录失败:', error);
            throw error;
        }
    }

    /**
     * 发起微信登录
     */
    async wechatLogin() {
        try {
            const response = await fetch(`${this.baseURL}/api/auth/wechat/login`);
            const data = await response.json();
            
            // 跳转到微信登录页面
            window.location.href = data.auth_url;
        } catch (error) {
            console.error('微信登录失败:', error);
            throw error;
        }
    }

    /**
     * 检查登录状态
     */
    isLoggedIn() {
        return !!this.token && !!this.user;
    }

    /**
     * 获取当前用户信息
     */
    getCurrentUser() {
        return this.user;
    }

    /**
     * 获取访问令牌
     */
    getToken() {
        return this.token;
    }

    /**
     * 登出
     */
    logout() {
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user_info');
        this.token = null;
        this.user = null;
        
        // 跳转到登录页面
        window.location.href = '/login';
    }

    /**
     * 保存用户信息到本地存储
     */
    saveUserInfo(token, user) {
        this.token = token;
        this.user = user;
        localStorage.setItem('auth_token', token);
        localStorage.setItem('user_info', JSON.stringify(user));
    }

    /**
     * 从URL参数获取登录信息
     */
    getLoginInfoFromURL() {
        const params = new URLSearchParams(window.location.search);
        return {
            token: params.get('token'),
            userId: params.get('user_id'),
            username: params.get('username'),
            email: params.get('email'),
            loginMethod: params.get('login_method')
        };
    }

    /**
     * 处理登录成功
     */
    handleLoginSuccess() {
        const loginInfo = this.getLoginInfoFromURL();
        
        if (loginInfo.token) {
            // 保存用户信息
            const user = {
                id: loginInfo.userId,
                username: loginInfo.username,
                email: loginInfo.email,
                loginMethod: loginInfo.loginMethod
            };
            
            this.saveUserInfo(loginInfo.token, user);
            
            // 清除URL参数
            window.history.replaceState({}, document.title, window.location.pathname);
            
            return true;
        }
        
        return false;
    }

    /**
     * 验证令牌
     */
    async validateToken() {
        if (!this.token) {
            return false;
        }

        try {
            const response = await fetch(`${this.baseURL}/api/auth/me`, {
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            if (response.ok) {
                const user = await response.json();
                this.user = user;
                localStorage.setItem('user_info', JSON.stringify(user));
                return true;
            } else {
                this.logout();
                return false;
            }
        } catch (error) {
            console.error('令牌验证失败:', error);
            this.logout();
            return false;
        }
    }

    /**
     * 创建带认证的请求
     */
    async authenticatedRequest(url, options = {}) {
        if (!this.isLoggedIn()) {
            throw new Error('用户未登录');
        }

        const defaultOptions = {
            headers: {
                'Authorization': `Bearer ${this.token}`,
                'Content-Type': 'application/json'
            }
        };

        const mergedOptions = {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultOptions.headers,
                ...options.headers
            }
        };

        const response = await fetch(url, mergedOptions);
        
        if (response.status === 401) {
            this.logout();
            throw new Error('登录已过期，请重新登录');
        }

        return response;
    }
}

// 创建全局实例
window.authService = new AuthService();

// 页面加载时检查登录状态
document.addEventListener('DOMContentLoaded', function() {
    // 检查是否有登录成功参数
    if (window.authService.handleLoginSuccess()) {
        console.log('登录成功！');
        // 可以在这里添加登录成功的处理逻辑
    } else {
        // 验证现有令牌
        window.authService.validateToken();
    }
});
