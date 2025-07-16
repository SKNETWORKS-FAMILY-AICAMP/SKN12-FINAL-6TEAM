declare global {
  interface Window {
    google: any;
  }
}

export interface User {
  id: number;
  email: string;
  google_id: string;
  name?: string;
  profile_picture?: string;
  is_first_login: boolean;
  created_at: string;
  updated_at: string;
}

export interface LoginResponse {
  user: User;
  access_token: string;
  token_type: string;
  is_first_login: boolean;
}

class AuthService {
  private baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
  private clientId = process.env.REACT_APP_GOOGLE_CLIENT_ID || '689738363605-i65c3ar97vnts2jeh648dj3v9b23njq4.apps.googleusercontent.com';
  private isGoogleLoaded = false;

  constructor() {
    console.log('AuthService initialized with:', {
      baseUrl: this.baseUrl,
      clientId: this.clientId?.substring(0, 20) + '...'
    });
    this.initializeGoogleAuth();
  }

  async initializeGoogleAuth() {
    try {
      // Google API가 로드될 때까지 기다리기
      await this.waitForGoogle();
      
      // Google Identity Services 초기화
      window.google.accounts.id.initialize({
        client_id: this.clientId,
        callback: this.handleCredentialResponse.bind(this),
      });
      
      this.isGoogleLoaded = true;
    } catch (error) {
      console.error('Google Auth initialization failed:', error);
    }
  }

  private waitForGoogle(): Promise<void> {
    return new Promise((resolve) => {
      if (window.google) {
        resolve();
        return;
      }
      
      const checkGoogle = () => {
        if (window.google) {
          resolve();
        } else {
          setTimeout(checkGoogle, 100);
        }
      };
      
      checkGoogle();
    });
  }


  private async handleCredentialResponse(response: any) {
    try {
      const loginResponse = await this.authenticateWithBackend(response.credential);
      if (loginResponse) {
        // 로그인 성공 후 리디렉션 처리
        if (loginResponse.is_first_login) {
          window.location.href = '/nickname';
        } else {
          window.location.href = '/main';
        }
      }
    } catch (error) {
      console.error('Authentication failed:', error);
    }
  }

  async signInWithGoogle(): Promise<LoginResponse | null> {
    try {
      if (!this.isGoogleLoaded) {
        await this.initializeGoogleAuth();
      }

      return new Promise((resolve) => {
        // Google One Tap 로그인 (팝업 없이)
        window.google.accounts.id.prompt((notification: any) => {
          if (notification.isNotDisplayed() || notification.isSkippedMoment()) {
            // One Tap이 표시되지 않으면 수동 로그인 버튼 표시
            this.showManualLoginButton(resolve);
          }
        });
      });
    } catch (error) {
      console.error('Google sign-in failed:', error);
      return null;
    }
  }

  private showManualLoginButton(resolve: any) {
    // 버튼을 수동으로 클릭할 수 있도록 표시
    const buttonElement = document.getElementById('google-signin-button');
    if (buttonElement) {
      buttonElement.classList.remove('hidden');
      window.google.accounts.id.renderButton(
        buttonElement,
        { 
          theme: 'outline', 
          size: 'large',
          type: 'standard',
          text: 'signin_with'
        }
      );
    }
    // 임시로 null 반환
    resolve(null);
  }


  async authenticateWithBackend(idToken: string): Promise<LoginResponse | null> {
    try {
      const response = await fetch(`${this.baseUrl}/auth/google`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          token: idToken,
        }),
      });

      if (!response.ok) {
        throw new Error('Backend authentication failed');
      }

      const loginResponse: LoginResponse = await response.json();
      
      // 토큰을 로컬 스토리지에 저장
      this.setAccessToken(loginResponse.access_token);
      this.setUserInfo(loginResponse.user);

      return loginResponse;
    } catch (error) {
      console.error('Backend authentication failed:', error);
      return null;
    }
  }

  async completeSignup(nickname: string): Promise<User | null> {
    try {
      const token = this.getAccessToken();
      console.log('Token for signup:', token?.substring(0, 20) + '...');
      
      if (!token) {
        throw new Error('No access token found');
      }

      const response = await fetch(`${this.baseUrl}/auth/complete-signup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          nickname: nickname,
        }),
      });

      console.log('Response status:', response.status);
      console.log('Response ok:', response.ok);

      if (!response.ok) {
        const errorData = await response.text();
        console.error('Response error:', errorData);
        throw new Error(`Signup completion failed: ${response.status} - ${errorData}`);
      }

      const updatedUser: User = await response.json();
      this.setUserInfo(updatedUser);

      return updatedUser;
    } catch (error) {
      console.error('Signup completion failed:', error);
      return null;
    }
  }

  async getCurrentUser(): Promise<User | null> {
    try {
      const token = this.getAccessToken();
      if (!token) {
        return null;
      }

      const response = await fetch(`${this.baseUrl}/auth/me`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        this.signOut();
        return null;
      }

      const user: User = await response.json();
      this.setUserInfo(user);

      return user;
    } catch (error) {
      console.error('Get current user failed:', error);
      this.signOut();
      return null;
    }
  }

  async signOut(): Promise<void> {
    try {
      if (window.google && window.google.accounts) {
        window.google.accounts.id.disableAutoSelect();
      }
      this.clearStoredData();
    } catch (error) {
      console.error('Sign out failed:', error);
      this.clearStoredData();
    }
  }

  isAuthenticated(): boolean {
    return !!this.getAccessToken();
  }

  isFirstLogin(): boolean {
    const user = this.getUserInfo();
    return user?.is_first_login ?? false;
  }

  private setAccessToken(token: string): void {
    localStorage.setItem('access_token', token);
  }

  private getAccessToken(): string | null {
    return localStorage.getItem('access_token');
  }

  private setUserInfo(user: User): void {
    localStorage.setItem('user_info', JSON.stringify(user));
  }

  private getUserInfo(): User | null {
    const userStr = localStorage.getItem('user_info');
    if (!userStr) return null;
    
    try {
      return JSON.parse(userStr);
    } catch {
      return null;
    }
  }

  private clearStoredData(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_info');
  }
}

export const authService = new AuthService();