(() => {
  const passwordButton = document.querySelector(".pcm-password-toggle");
  const passwordInput = document.querySelector("#id_password");
  if (passwordButton && passwordInput) {
    passwordButton.addEventListener("click", () => {
      const visible = passwordInput.type === "text";
      passwordInput.type = visible ? "password" : "text";
      passwordButton.textContent = visible ? "Tampilkan" : "Sembunyikan";
      passwordButton.setAttribute("aria-label", visible ? "Tampilkan password" : "Sembunyikan password");
      passwordButton.setAttribute("aria-pressed", String(!visible));
    });
  }

  const loginForm = document.querySelector("#login-form");
  if (loginForm) {
    loginForm.addEventListener("submit", () => {
      const submit = loginForm.querySelector(".pcm-login-submit");
      if (submit) {
        submit.classList.add("is-loading");
        submit.disabled = true;
      }
    });
  }

  const navFilter = document.querySelector("#nav-filter");
  if (navFilter) {
    const items = [...document.querySelectorAll(".pcm-nav-group li")];
    navFilter.addEventListener("input", () => {
      const value = navFilter.value.trim().toLocaleLowerCase();
      items.forEach((item) => {
        item.hidden = !item.textContent.toLocaleLowerCase().includes(value);
      });
      document.querySelectorAll(".pcm-nav-group").forEach((group) => {
        group.hidden = ![...group.querySelectorAll("li")].some((item) => !item.hidden);
      });
    });
  }
})();
