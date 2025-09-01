class Login {
    constructor() {
        this.init();
    }

    init() {
        this.loginForm = document.getElementById("loginForm");
    }

    login() {
        this.loginForm.submit();
    }
}