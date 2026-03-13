const API_URL = "http://localhost:8000/api";
let currentMode = "login";

const authSection = document.getElementById("auth-section");
const dashboardSection = document.getElementById("dashboard-section");
const authForm = document.getElementById("auth-form");
const authError = document.getElementById("auth-error");
const authBtn = document.getElementById("auth-btn");
const emailGroup = document.getElementById("email-group");

const tasksList = document.getElementById("tasks-list");
const categoriesList = document.getElementById("categories-list");
const categorySelect = document.getElementById("task-category");

window.addEventListener("DOMContentLoaded", () => {
  const token = localStorage.getItem("access_token");
  if (token) {
    showDashboard();
  } else {
    showAuth();
  }
});

function switchTab(mode) {
  currentMode = mode;
  document
    .getElementById("tab-login")
    .classList.toggle("active", mode === "login");
  document
    .getElementById("tab-register")
    .classList.toggle("active", mode === "register");

  authBtn.textContent = mode === "login" ? "Login" : "Register";
  emailGroup.style.display = mode === "register" ? "block" : "none";
  authError.textContent = "";
}

function showAuth() {
  authSection.style.display = "block";
  dashboardSection.style.display = "none";
}

function showDashboard() {
  authSection.style.display = "none";
  dashboardSection.style.display = "block";
  fetchCategories();
  fetchTasks();
}

function logout() {
  localStorage.removeItem("access_token");
  showAuth();
}

authForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;
  const email = document.getElementById("email").value;

  authError.textContent = "";

  try {
    if (currentMode === "login") {
      const formData = new FormData();
      formData.append("username", username);
      formData.append("password", password);

      const res = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        body: formData,
      });
      const data = await res.json();

      if (!res.ok) throw new Error(data.detail || "Login failed");

      localStorage.setItem("access_token", data.access_token);
      showDashboard();
    } else {
      const res = await fetch(`${API_URL}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email, password: password }),
      });
      const data = await res.json();

      if (!res.ok) throw new Error(data.detail || "Registration failed");

      alert("Registration successful! Please login.");
      switchTab("login");
    }
  } catch (err) {
    authError.textContent = err.message;
  }
});

async function fetchCategories() {
  const token = localStorage.getItem("access_token");
  try {
    const res = await fetch(`${API_URL}/categories/get-categories?limit=50`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    const data = await res.json();

    categoriesList.innerHTML = "";
    categorySelect.innerHTML = '<option value="">No Category</option>';

    if (data.items) {
      data.items.forEach((cat) => {
        const li = document.createElement("li");
        li.textContent = cat.name;
        categoriesList.appendChild(li);

        const opt = document.createElement("option");
        opt.value = cat.id;
        opt.textContent = cat.name;
        categorySelect.appendChild(opt);
      });
    }
  } catch (e) {
    console.error("Error fetching categories", e);
  }
}

async function fetchTasks() {
  const token = localStorage.getItem("access_token");
  try {
    const res = await fetch(`${API_URL}/tasks/?limit=50`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    const data = await res.json();

    tasksList.innerHTML = "";
    if (data.items) {
      data.items.forEach((task) => {
        const el = document.createElement("div");
        el.className = "task-item";
        el.innerHTML = `
                    <div class="task-content">
                        <div class="task-title">${task.title}</div>
                        ${task.description ? `<div class="task-desc">${task.description}</div>` : ""}
                        <div class="task-meta">
                            <span>Priority: ${task.priority}</span>
                            <span>Status: ${task.status}</span>
                            ${task.category ? `<span>Category: ${task.category.name}</span>` : ""}
                        </div>
                    </div>
                    <div class="task-actions">
                        <button class="btn-danger" onclick="deleteTask(${task.id})">Delete</button>
                    </div>
                `;
        tasksList.appendChild(el);
      });
    }
  } catch (e) {
    console.error("Error fetching tasks", e);
  }
}

document
  .getElementById("create-category-form")
  .addEventListener("submit", async (e) => {
    e.preventDefault();
    const name = document.getElementById("new-category-name").value;
    const token = localStorage.getItem("access_token");

    try {
      const res = await fetch(`${API_URL}/categories/create-category`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ name }),
      });
      if (res.ok) {
        document.getElementById("new-category-name").value = "";
        fetchCategories();
      }
    } catch (e) {
      console.error(e);
    }
  });

document
  .getElementById("create-task-form")
  .addEventListener("submit", async (e) => {
    e.preventDefault();
    const title = document.getElementById("task-title").value;
    const desc = document.getElementById("task-desc").value;
    const catId = document.getElementById("task-category").value;
    const priority = document.getElementById("task-priority").value;
    const token = localStorage.getItem("access_token");

    const payload = {
      title,
      description: desc || null,
      priority: priority,
      status: "not_started",
      tags: [],
    };
    if (catId) {
      payload.category_id = parseInt(catId);
    }

    try {
      const res = await fetch(`${API_URL}/tasks/create-task`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });
      if (res.ok) {
        document.getElementById("task-title").value = "";
        document.getElementById("task-desc").value = "";
        fetchTasks();
      }
    } catch (e) {
      console.error(e);
    }
  });

async function deleteTask(id) {
  if (!confirm("Delete this task?")) return;
  const token = localStorage.getItem("access_token");
  try {
    const res = await fetch(`${API_URL}/tasks/${id}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` },
    });
    if (res.ok) {
      fetchTasks();
    }
  } catch (e) {
    console.error(e);
  }
}
