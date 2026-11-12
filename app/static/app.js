// Recipe Book Frontend Application

const API_BASE = '/api';

// Application State
const state = {
  recipes: [],
  categories: [],
  subcategories: [],
  activeCategory: '',
  activeSubcategory: '',
  searchQuery: '',
  viewOnlyFav: false,
  currentUser: null,
  token: localStorage.getItem('access_token') || null,
  currentModalRecipeId: null,
  timerInterval: null,
  timerSeconds: 0,
  timerRunning: false,
};

// DOM Elements
const elements = {
  recipesGrid: document.getElementById('recipesGrid'),
  recipeCount: document.getElementById('recipeCount'),
  emptyState: document.getElementById('emptyState'),
  searchInput: document.getElementById('searchInput'),
  searchInputMobile: document.getElementById('searchInputMobile'),
  clearSearchBtn: document.getElementById('clearSearchBtn'),
  subcategoriesContainer: document.getElementById('subcategoriesContainer'),
  mainCategoriesContainer: document.getElementById('mainCategoriesContainer'),
  viewAllBtn: document.getElementById('viewAllBtn'),
  viewFavBtn: document.getElementById('viewFavBtn'),
  favoritesTabBtn: document.getElementById('favoritesTabBtn'),
  favCountBadge: document.getElementById('favCountBadge'),
  authSection: document.getElementById('authSection'),
  resetFiltersBtn: document.getElementById('resetFiltersBtn'),

  // Detail Modal
  recipeDetailModal: document.getElementById('recipeDetailModal'),
  closeDetailModalBtn: document.getElementById('closeDetailModalBtn'),
  closeDetailModalFooterBtn: document.getElementById('closeDetailModalFooterBtn'),
  detailImage: document.getElementById('detailImage'),
  detailTitle: document.getElementById('detailTitle'),
  detailCategory: document.getElementById('detailCategory'),
  detailSubcategory: document.getElementById('detailSubcategory'),
  detailDescription: document.getElementById('detailDescription'),
  detailIngredientsList: document.getElementById('detailIngredientsList'),
  detailStepsList: document.getElementById('detailStepsList'),
  ingredientsCount: document.getElementById('ingredientsCount'),
  stepsCount: document.getElementById('stepsCount'),
  detailCreatedAt: document.getElementById('detailCreatedAt'),
  detailAuthorBadge: document.getElementById('detailAuthorBadge'),
  detailFavBtn: document.getElementById('detailFavBtn'),
  detailFavText: document.getElementById('detailFavText'),
  deleteRecipeBtn: document.getElementById('deleteRecipeBtn'),

  // Comments and Ratings
  detailCommentsCountBadge: document.getElementById('detailCommentsCountBadge'),
  detailAverageRatingBadge: document.getElementById('detailAverageRatingBadge'),
  detailAvgRatingStars: document.getElementById('detailAvgRatingStars'),
  detailAvgRatingNumber: document.getElementById('detailAvgRatingNumber'),
  addCommentContainer: document.getElementById('addCommentContainer'),
  detailCommentsList: document.getElementById('detailCommentsList'),

  // Timer
  timerDisplay: document.getElementById('timerDisplay'),
  timerToggleBtn: document.getElementById('timerToggleBtn'),
  timerResetBtn: document.getElementById('timerResetBtn'),

  // Create Modal (Admin Only)
  openCreateModalBtn: document.getElementById('openCreateModalBtn'),
  recipeCreateModal: document.getElementById('recipeCreateModal'),
  closeCreateModalBtn: document.getElementById('closeCreateModalBtn'),
  cancelCreateModalBtn: document.getElementById('cancelCreateModalBtn'),
  createRecipeForm: document.getElementById('createRecipeForm'),
  formRecipeCategorySelect: document.getElementById('formRecipeCategorySelect'),
  formRecipeCategoryCustom: document.getElementById('formRecipeCategoryCustom'),
  formRecipeSubcatSelect: document.getElementById('formRecipeSubcatSelect'),
  formRecipeSubcatCustom: document.getElementById('formRecipeSubcatCustom'),
  ingredientsRowsContainer: document.getElementById('ingredientsRowsContainer'),
  stepsRowsContainer: document.getElementById('stepsRowsContainer'),
  addIngredientRowBtn: document.getElementById('addIngredientRowBtn'),
  addStepRowBtn: document.getElementById('addStepRowBtn'),
  formErrorMessage: document.getElementById('formErrorMessage'),

  // File Upload
  formRecipeImage: document.getElementById('formRecipeImage'),
  imageDropzone: document.getElementById('imageDropzone'),
  recipeFileInput: document.getElementById('recipeFileInput'),
  dropzoneEmptyContent: document.getElementById('dropzoneEmptyContent'),
  dropzoneLoadingContent: document.getElementById('dropzoneLoadingContent'),
  dropzonePreviewContent: document.getElementById('dropzonePreviewContent'),
  uploadPreviewImg: document.getElementById('uploadPreviewImg'),
  uploadPreviewFilename: document.getElementById('uploadPreviewFilename'),
  uploadPreviewSize: document.getElementById('uploadPreviewSize'),
  removeUploadedFileBtn: document.getElementById('removeUploadedFileBtn'),
  toggleExternalUrlBtn: document.getElementById('toggleExternalUrlBtn'),
  externalUrlBox: document.getElementById('externalUrlBox'),
  formRecipeExternalUrl: document.getElementById('formRecipeExternalUrl'),

  // Auth Modal
  authModal: document.getElementById('authModal'),
  authForm: document.getElementById('authForm'),
  authTabLogin: document.getElementById('authTabLogin'),
  authTabRegister: document.getElementById('authTabRegister'),
  authModalTitle: document.getElementById('authModalTitle'),
  authUsername: document.getElementById('authUsername'),
  authPassword: document.getElementById('authPassword'),
  authSubmitBtn: document.getElementById('authSubmitBtn'),
  authErrorMsg: document.getElementById('authErrorMsg'),
  closeAuthModalBtn: document.getElementById('closeAuthModalBtn'),

  // Toasts
  toastContainer: document.getElementById('toastContainer'),
};

// Helper: HTTP Fetch with Auth
async function apiRequest(endpoint, options = {}) {
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };

  if (state.token) {
    headers['Authorization'] = `Bearer ${state.token}`;
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 401 && state.token) {
    logout();
    showToast('Сессия истекла. Войдите снова.', 'error');
    throw new Error('Unauthorized');
  }

  return response;
}

// Toast Notifications
function showToast(message, type = 'info') {
  const toast = document.createElement('div');
  const colors = {
    info: 'bg-stone-900 text-stone-100',
    success: 'bg-stone-900 text-emerald-400 border border-stone-800',
    error: 'bg-rose-950 text-rose-200 border border-rose-900',
  };
  toast.className = `px-4 py-3 rounded-2xl shadow-2xl text-xs font-medium flex items-center gap-2.5 pointer-events-auto transform translate-y-2 opacity-0 transition-all duration-200 ${colors[type] || colors.info}`;
  
  const icon = type === 'success' ? 'check-circle-2' : type === 'error' ? 'alert-triangle' : 'info';
  toast.innerHTML = `<i data-lucide="${icon}" class="w-4 h-4 flex-shrink-0"></i> <span>${message}</span>`;
  
  elements.toastContainer.appendChild(toast);
  lucide.createIcons({ root: toast });

  setTimeout(() => {
    toast.classList.remove('translate-y-2', 'opacity-0');
  }, 10);

  setTimeout(() => {
    toast.classList.add('opacity-0', 'translate-y-2');
    setTimeout(() => toast.remove(), 250);
  }, 3500);
}

// Auth Lifecycle & Admin Gate
async function checkAuth() {
  if (!state.token) {
    renderAuthSection();
    return;
  }

  try {
    const res = await apiRequest('/auth/me');
    if (res.ok) {
      state.currentUser = await res.json();
      updateFavBadge();
    } else {
      logout();
    }
  } catch (err) {
    state.currentUser = null;
  }
  renderAuthSection();
}

function renderAuthSection() {
  const isAdmin = state.currentUser?.role === 'admin';

  // "Добавить рецепт" button is accessible to all (prompts login if guest)
  elements.openCreateModalBtn.classList.remove('hidden');
  elements.openCreateModalBtn.classList.add('flex');

  if (state.currentUser) {
    elements.authSection.innerHTML = `
      <div class="flex items-center gap-2 pl-2">
        <div class="flex items-center gap-1.5 px-3.5 py-1.5 rounded-full bg-brand-50 border border-brand-200/60 text-brand-900 text-xs font-semibold">
          <i data-lucide="user" class="w-3.5 h-3.5 text-brand-600"></i>
          <span>${state.currentUser.username}</span>
          ${isAdmin ? '<span class="bg-brand-600 text-white text-[10px] px-1.5 py-0.2 rounded-full font-bold ml-1">Admin</span>' : ''}
        </div>
        <button id="logoutBtn" class="text-stone-400 hover:text-stone-700 p-1.5 rounded-full hover:bg-stone-100 transition-colors" title="Выйти">
          <i data-lucide="log-out" class="w-4 h-4"></i>
        </button>
      </div>
    `;
    document.getElementById('logoutBtn')?.addEventListener('click', logout);
  } else {
    elements.authSection.innerHTML = `
      <button id="loginBtn" class="px-4 py-2 text-xs font-semibold text-stone-800 border border-stone-300 hover:border-brand-600 hover:text-brand-600 rounded-full transition-colors">
        Войти
      </button>
    `;
    document.getElementById('loginBtn')?.addEventListener('click', () => openAuthModal('login'));
  }
  lucide.createIcons({ root: elements.authSection });
}

function logout() {
  state.token = null;
  state.currentUser = null;
  localStorage.removeItem('access_token');
  renderAuthSection();
  updateFavBadge();
  loadRecipes();
  showToast('Вы вышли из системы');
}

function updateFavBadge() {
  const count = state.currentUser?.favourite_recipe_ids?.length || 0;
  if (count > 0) {
    elements.favCountBadge.textContent = count;
    elements.favCountBadge.classList.remove('hidden');
  } else {
    elements.favCountBadge.classList.add('hidden');
  }
}

// Fetch Categories & Subcategories
async function loadCategories() {
  try {
    const res = await apiRequest('/recipes/categories');
    if (res.ok) {
      const data = await res.json();
      state.categories = data.categories;
      state.subcategories = data.subcategories;
      renderFilterControls();
      populateFormCategorySelects();
    }
  } catch (err) {
    console.error('Failed to load categories', err);
  }
}

function renderFilterControls() {
  // Clean Subcategory Tabs (No clown emojis)
  const subcatHtml = [
    `<button class="subcat-pill ${state.activeSubcategory === '' ? 'active' : ''}" data-subcat="">Все</button>`
  ];

  state.subcategories.forEach(sub => {
    const active = state.activeSubcategory.toLowerCase() === sub.toLowerCase() ? 'active' : '';
    // Format capitalize first letter
    const label = sub.charAt(0).toUpperCase() + sub.slice(1);
    subcatHtml.push(
      `<button class="subcat-pill ${active}" data-subcat="${sub}">${label}</button>`
    );
  });
  elements.subcategoriesContainer.innerHTML = subcatHtml.join('');

  elements.subcategoriesContainer.querySelectorAll('.subcat-pill').forEach(btn => {
    btn.addEventListener('click', () => {
      state.activeSubcategory = btn.getAttribute('data-subcat');
      renderFilterControls();
      loadRecipes();
    });
  });

  // Main Category Chips
  const catHtml = [
    `<span class="category-chip ${state.activeCategory === '' ? 'active' : ''}" data-cat="">Все категории</span>`
  ];
  state.categories.forEach(cat => {
    const active = state.activeCategory.toLowerCase() === cat.toLowerCase() ? 'active' : '';
    catHtml.push(
      `<span class="category-chip ${active}" data-cat="${cat}">${cat}</span>`
    );
  });
  elements.mainCategoriesContainer.innerHTML = `<span class="text-stone-400 font-medium">Категория:</span>` + catHtml.join('');

  elements.mainCategoriesContainer.querySelectorAll('.category-chip').forEach(btn => {
    btn.addEventListener('click', () => {
      state.activeCategory = btn.getAttribute('data-cat');
      renderFilterControls();
      loadRecipes();
    });
  });
}

function populateFormCategorySelects() {
  const catSelect = elements.formRecipeCategorySelect;
  const currentVal = catSelect.value;
  catSelect.innerHTML = state.categories
    .map(c => `<option value="${c}">${c}</option>`)
    .join('') + `<option value="__custom__">+ Своя категория...</option>`;
  if (currentVal && currentVal !== '__custom__') catSelect.value = currentVal;

  const subcatSelect = elements.formRecipeSubcatSelect;
  const currentSubVal = subcatSelect.value;
  subcatSelect.innerHTML = `<option value="">Без подкатегории</option>` +
    state.subcategories
      .map(s => `<option value="${s}">${s.charAt(0).toUpperCase() + s.slice(1)}</option>`)
      .join('') + `<option value="__custom__">+ Своя подкатегория...</option>`;
  if (currentSubVal && currentSubVal !== '__custom__') subcatSelect.value = currentSubVal;
}

// Fetch and Render Recipes
async function loadRecipes() {
  elements.recipeCount.innerHTML = `<span class="text-stone-400">Загрузка...</span>`;

  let endpoint = '/recipes?';
  const params = new URLSearchParams();

  if (state.viewOnlyFav && state.currentUser) {
    endpoint = '/users/me/favourites?';
  } else {
    if (state.activeCategory) params.append('category', state.activeCategory);
    if (state.activeSubcategory) params.append('subcategory', state.activeSubcategory);
    if (state.searchQuery) params.append('search', state.searchQuery);
  }

  try {
    const res = await apiRequest(`${endpoint}${params.toString()}`);
    if (res.ok) {
      let recipes = await res.json();
      
      if (state.viewOnlyFav && !state.currentUser) {
        recipes = [];
      } else if (state.viewOnlyFav && (state.activeCategory || state.activeSubcategory || state.searchQuery)) {
        recipes = recipes.filter(r => {
          if (state.activeCategory && r.category.toLowerCase() !== state.activeCategory.toLowerCase()) return false;
          if (state.activeSubcategory && (!r.subcategory || r.subcategory.toLowerCase() !== state.activeSubcategory.toLowerCase())) return false;
          if (state.searchQuery && !r.name.toLowerCase().includes(state.searchQuery.toLowerCase())) return false;
          return true;
        });
      }

      state.recipes = recipes;
      renderRecipesGrid(recipes);
    } else {
      showToast('Ошибка при загрузке рецептов', 'error');
    }
  } catch (err) {
    console.error(err);
    elements.recipeCount.textContent = 'Ошибка загрузки';
  }
}

function renderRecipesGrid(recipes) {
  elements.recipeCount.textContent = `Рецептов в каталоге: ${recipes.length}`;

  if (recipes.length === 0) {
    elements.recipesGrid.innerHTML = '';
    elements.emptyState.classList.remove('hidden');
    return;
  }

  elements.emptyState.classList.add('hidden');

  elements.recipesGrid.innerHTML = recipes
    .map(recipe => {
      const fallbackImg = `https://images.unsplash.com/photo-1495521821757-a1efb6729352?auto=format&fit=crop&w=800&q=80`;
      const imgUrl = recipe.image_path && recipe.image_path.trim() ? recipe.image_path : fallbackImg;
      const isFav = recipe.is_favourite || false;
      const ingCount = recipe.ingredients?.length || 0;
      const stepsCount = recipe.steps?.length || 0;

      return `
        <article class="recipe-card rounded-3xl overflow-hidden flex flex-col group cursor-pointer" data-id="${recipe.id}">
          
          <!-- Image Container -->
          <div class="relative aspect-[16/11] w-full bg-stone-100 overflow-hidden">
            <img 
              src="${imgUrl}" 
              alt="${recipe.name}" 
              loading="lazy"
              onerror="this.src='${fallbackImg}'"
              class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700 ease-out" 
            />
            <div class="absolute inset-0 bg-gradient-to-t from-stone-950/40 via-transparent to-transparent"></div>
            
            <!-- Category Tag in Image -->
            <div class="absolute top-3.5 left-3.5 flex items-center gap-1.5 flex-wrap">
              <span class="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-white/95 text-stone-900 shadow-sm backdrop-blur-sm">
                ${recipe.category}
              </span>
              ${recipe.subcategory ? `<span class="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-brand-600 text-white shadow-sm">${recipe.subcategory}</span>` : ''}
            </div>

            <!-- Bookmark Button -->
            <button 
              class="fav-toggle-btn absolute top-3.5 right-3.5 w-8 h-8 rounded-full bg-white/90 hover:bg-white text-stone-700 flex items-center justify-center backdrop-blur-sm transition-all active:scale-95 shadow-sm"
              data-id="${recipe.id}"
              title="${isFav ? 'В избранном' : 'Добавить в избранное'}"
            >
              <i data-lucide="bookmark" class="w-4 h-4 ${isFav ? 'fill-brand-600 text-brand-600' : 'text-stone-400 hover:text-stone-600'}"></i>
            </button>
          </div>

          <!-- Card Body -->
          <div class="p-6 flex-1 flex flex-col justify-between">
            <div>
              <!-- Author and Rating Meta -->
              <div class="flex items-center justify-between gap-2 mb-2 text-[11px]">
                <span class="text-stone-400 font-medium truncate">
                  ${recipe.author_username ? `от @${recipe.author_username}` : 'Рецепт шефа'}
                </span>
                <div class="flex items-center gap-1 font-bold ${recipe.ratings_count > 0 ? 'text-amber-700 bg-amber-50/90 px-2 py-0.5 rounded-full border border-amber-200/60' : 'text-stone-400'}">
                  <i data-lucide="star" class="w-3 h-3 ${recipe.ratings_count > 0 ? 'fill-amber-400 text-amber-500' : 'text-stone-300'}"></i>
                  <span>${recipe.ratings_count > 0 ? `${recipe.rating.toFixed(1)} (${recipe.ratings_count})` : 'Новый'}</span>
                </div>
              </div>

              <h3 class="font-serif text-xl font-semibold text-stone-900 group-hover:text-brand-600 transition-colors leading-snug mb-2 line-clamp-1">
                ${recipe.name}
              </h3>
              
              <p class="text-xs text-stone-500 line-clamp-2 leading-relaxed font-light mb-4">
                ${recipe.description}
              </p>
            </div>

            <!-- Meta Row -->
            <div class="pt-4 border-t border-stone-100 flex items-center justify-between text-xs text-stone-400">
              <span class="font-medium text-stone-500">${ingCount} ингр. • ${stepsCount} шагов</span>
              <span class="font-bold text-brand-600 group-hover:text-brand-700 group-hover:translate-x-0.5 transition-all inline-flex items-center gap-1">
                Приготовить <i data-lucide="arrow-right" class="w-3.5 h-3.5"></i>
              </span>
            </div>

          </div>

        </article>
      `;
    })
    .join('');

  lucide.createIcons({ root: elements.recipesGrid });

  // Bind clicks
  elements.recipesGrid.querySelectorAll('.recipe-card').forEach(card => {
    card.addEventListener('click', (e) => {
      if (e.target.closest('.fav-toggle-btn')) return;
      const id = card.getAttribute('data-id');
      openRecipeDetail(id);
    });
  });

  elements.recipesGrid.querySelectorAll('.fav-toggle-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const id = btn.getAttribute('data-id');
      handleToggleFavourite(id);
    });
  });
}

// Favorite Toggle
async function handleToggleFavourite(recipeId) {
  if (!state.currentUser) {
    openAuthModal('login');
    showToast('Войдите в аккаунт, чтобы сохранять в избранное');
    return;
  }

  try {
    const res = await apiRequest(`/recipes/${recipeId}/favourite`, {
      method: 'POST',
    });
    if (res.ok) {
      const data = await res.json();
      const isFav = data.favourite;

      const target = state.recipes.find(r => r.id === parseInt(recipeId, 10));
      if (target) target.is_favourite = isFav;

      if (isFav) {
        if (!state.currentUser.favourite_recipe_ids.includes(parseInt(recipeId, 10))) {
          state.currentUser.favourite_recipe_ids.push(parseInt(recipeId, 10));
        }
        showToast('Добавлено в избранное');
      } else {
        state.currentUser.favourite_recipe_ids = state.currentUser.favourite_recipe_ids.filter(
          id => id !== parseInt(recipeId, 10)
        );
        showToast('Удалено из избранного');
      }

      updateFavBadge();

      if (state.currentModalRecipeId === parseInt(recipeId, 10)) {
        updateModalFavButton(isFav);
      }

      renderRecipesGrid(state.recipes);
    }
  } catch (err) {
    showToast('Не удалось обновить статус избранного', 'error');
  }
}

function updateModalFavButton(isFav) {
  elements.detailFavBtn.innerHTML = `
    <i data-lucide="bookmark" class="w-3.5 h-3.5 ${isFav ? 'fill-brand-600 text-brand-600' : 'text-stone-500'}"></i>
    <span class="${isFav ? 'text-brand-700 font-bold' : ''}">${isFav ? 'В избранном' : 'В избранное'}</span>
  `;
  lucide.createIcons({ root: elements.detailFavBtn });
}

// Recipe Detail Modal
async function openRecipeDetail(recipeId) {
  state.currentModalRecipeId = parseInt(recipeId, 10);
  elements.recipeDetailModal.classList.remove('hidden');

  try {
    const res = await apiRequest(`/recipes/${recipeId}`);
    if (res.ok) {
      const recipe = await res.json();
      const fallbackImg = `https://images.unsplash.com/photo-1495521821757-a1efb6729352?auto=format&fit=crop&w=1200&q=80`;
      elements.detailImage.src = recipe.image_path && recipe.image_path.trim() ? recipe.image_path : fallbackImg;
      elements.detailImage.onerror = () => { elements.detailImage.src = fallbackImg; };
      elements.detailTitle.textContent = recipe.name;
      elements.detailCategory.textContent = recipe.category;

      if (recipe.subcategory) {
        elements.detailSubcategory.textContent = recipe.subcategory;
        elements.detailSubcategory.classList.remove('hidden');
      } else {
        elements.detailSubcategory.classList.add('hidden');
      }

      elements.detailDescription.textContent = recipe.description;
      elements.ingredientsCount.textContent = `${recipe.ingredients.length} позиций`;
      elements.stepsCount.textContent = `${recipe.steps.length} шагов`;

      const date = new Date(recipe.created_at);
      elements.detailCreatedAt.textContent = `Добавлен: ${date.toLocaleDateString('ru-RU')}`;

      // Ingredients List
      elements.detailIngredientsList.innerHTML = recipe.ingredients
        .map(ing => {
          const unitStr = ing.unit ? `${ing.unit.quantity} ${ing.unit.name}` : '';
          return `
            <li class="flex items-center justify-between py-2 px-3 rounded-xl bg-stone-50 border border-stone-100 text-xs">
              <label class="flex items-center gap-2.5 cursor-pointer flex-1">
                <input type="checkbox" class="ingredient-checkbox w-3.5 h-3.5 rounded text-stone-900 focus:ring-0 border-stone-300">
                <span class="font-medium text-stone-800">${ing.name}</span>
              </label>
              ${unitStr ? `<span class="text-stone-500 font-medium text-[11px]">${unitStr}</span>` : ''}
            </li>
          `;
        })
        .join('');

      // Steps List
      elements.detailStepsList.innerHTML = recipe.steps
        .map(st => `
          <li class="p-4 rounded-2xl bg-stone-50 border border-stone-100 flex items-start gap-3.5">
            <input type="checkbox" class="step-checkbox mt-1 w-4 h-4 rounded text-stone-900 focus:ring-0 border-stone-300 cursor-pointer">
            <div class="step-content flex-1">
              <div class="text-xs font-semibold text-stone-900 mb-1">Шаг ${st.number}</div>
              <p class="text-xs text-stone-600 leading-relaxed font-light">${st.text}</p>
            </div>
          </li>
        `)
        .join('');

      updateModalFavButton(recipe.is_favourite);
      elements.detailFavBtn.onclick = () => handleToggleFavourite(recipe.id);

      // Author Badge in footer
      if (recipe.author_username) {
        elements.detailAuthorBadge.textContent = `• Автор: @${recipe.author_username}`;
        elements.detailAuthorBadge.classList.remove('hidden');
      } else {
        elements.detailAuthorBadge.classList.add('hidden');
      }

      // Delete button: visible for admin OR author of the recipe
      const isAuthor = Boolean(state.currentUser && recipe.author_id && state.currentUser.id === recipe.author_id);
      const isAdmin = state.currentUser?.role === 'admin';
      if (isAdmin || isAuthor) {
        elements.deleteRecipeBtn.classList.remove('hidden');
        elements.deleteRecipeBtn.onclick = () => handleDeleteRecipe(recipe.id);
      } else {
        elements.deleteRecipeBtn.classList.add('hidden');
      }

      // Update Rating summary in Detail modal
      updateModalRatingSummary(recipe.rating, recipe.ratings_count);

      // Render Comment submission box and load existing comments
      renderAddCommentBox(recipe.id);
      await loadRecipeComments(recipe.id);

      lucide.createIcons({ root: elements.recipeDetailModal });
    }
  } catch (err) {
    showToast('Не удалось загрузить данные рецепта', 'error');
  }
}

function updateModalRatingSummary(avgRating, count) {
  const countVal = count || 0;
  elements.detailCommentsCountBadge.textContent = countVal;
  if (countVal > 0) {
    elements.detailAvgRatingStars.innerHTML = renderStarIcons(avgRating, 'w-4 h-4');
    elements.detailAvgRatingNumber.textContent = `${avgRating.toFixed(1)} / 5.0 (${countVal})`;
  } else {
    elements.detailAvgRatingStars.innerHTML = renderStarIcons(0, 'w-4 h-4');
    elements.detailAvgRatingNumber.textContent = 'Нет оценок';
  }
}

function closeRecipeDetail() {
  elements.recipeDetailModal.classList.add('hidden');
  state.currentModalRecipeId = null;
}

// Delete Recipe (Author or Admin)
async function handleDeleteRecipe(recipeId) {
  if (!confirm('Вы уверены, что хотите удалить этот рецепт?')) return;

  try {
    const res = await apiRequest(`/recipes/${recipeId}`, { method: 'DELETE' });
    if (res.status === 204 || res.ok) {
      showToast('Рецепт удален');
      closeRecipeDetail();
      loadRecipes();
      loadCategories();
    } else {
      showToast('Ошибка при удалении рецепта', 'error');
    }
  } catch (err) {
    showToast('Ошибка при удалении', 'error');
  }
}

// --- Comments and Star Rating Helpers ---

function renderStarIcons(rating, sizeClass = 'w-4 h-4') {
  let html = '<div class="inline-flex items-center gap-0.5">';
  const r = typeof rating === 'number' ? rating : 0;
  for (let i = 1; i <= 5; i++) {
    let fillWidthPercent = 0;
    if (r >= i) {
      fillWidthPercent = 100;
    } else if (r >= i - 0.5) {
      fillWidthPercent = 50;
    } else {
      fillWidthPercent = 0;
    }

    html += `
      <div class="relative ${sizeClass} text-stone-200 flex-shrink-0">
        <svg class="w-full h-full fill-stone-200 text-stone-200" viewBox="0 0 24 24">
          <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
        </svg>
        <div class="star-clip" style="width: ${fillWidthPercent}%;">
          <svg class="${sizeClass} fill-amber-400 text-amber-500" viewBox="0 0 24 24">
            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
          </svg>
        </div>
      </div>
    `;
  }
  html += '</div>';
  return html;
}

let currentPickerRating = 5.0;

function renderAddCommentBox(recipeId) {
  if (!state.currentUser) {
    elements.addCommentContainer.innerHTML = `
      <div class="flex items-center justify-between flex-wrap gap-4">
        <div>
          <div class="text-xs font-semibold text-stone-900">Оцените этот рецепт</div>
          <div class="text-[11px] text-stone-500 font-light mt-0.5">Войдите в систему, чтобы поставить оценку от 1 до 5 звезд и поделиться отзывом.</div>
        </div>
        <button id="commentLoginPromptBtn" class="px-4 py-2 bg-stone-900 hover:bg-black text-white rounded-full text-xs font-semibold shadow-sm transition-all">
          Войти в аккаунт
        </button>
      </div>
    `;
    document.getElementById('commentLoginPromptBtn')?.addEventListener('click', () => openAuthModal('login'));
    return;
  }

  currentPickerRating = 5.0;

  elements.addCommentContainer.innerHTML = `
    <div class="space-y-4">
      <div class="flex items-center justify-between flex-wrap gap-2">
        <div class="flex items-center gap-3">
          <span class="text-xs font-semibold uppercase tracking-wider text-stone-700">Ваша оценка:</span>
          <div id="interactiveRatingPicker" class="star-rating-picker" title="Нажмите на левую половину звезды для 0.5">
            ${[1, 2, 3, 4, 5]
              .map(
                starNum => `
              <div class="star-picker-item" data-star="${starNum}">
                <svg class="w-full h-full fill-stone-200 text-stone-200" viewBox="0 0 24 24">
                  <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
                </svg>
                <div class="star-clip" style="width: 100%;">
                  <svg class="w-full h-full fill-amber-400 text-amber-500" viewBox="0 0 24 24">
                    <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
                  </svg>
                </div>
              </div>
            `
              )
              .join('')}
          </div>
          <span id="ratingDisplayValue" class="text-xs font-bold px-2 py-0.5 rounded-md bg-amber-100/90 text-amber-900 border border-amber-300 font-mono">5.0 / 5</span>
        </div>
        <span class="text-[11px] text-stone-400 font-light">Кликните по середине звезды для оценки с половиной (напр. 4.5)</span>
      </div>

      <textarea 
        id="commentTextInput" 
        rows="2" 
        placeholder="Поделитесь вашим кулинарным опытом, пропорциями или впечатлениями..." 
        class="w-full px-4 py-2.5 text-xs bg-white border border-stone-200 rounded-xl outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20 transition-all resize-none text-stone-800"
      ></textarea>

      <div class="flex items-center justify-between">
        <span id="commentErrorMsg" class="hidden text-xs text-rose-600 font-medium"></span>
        <button 
          id="submitCommentBtn" 
          class="ml-auto px-5 py-2 bg-brand-600 hover:bg-brand-500 text-white rounded-full text-xs font-bold shadow-sm shadow-brand-600/20 active:scale-95 transition-all flex items-center gap-1.5"
        >
          <i data-lucide="send" class="w-3.5 h-3.5"></i>
          <span>Оставить отзыв</span>
        </button>
      </div>
    </div>
  `;

  lucide.createIcons({ root: elements.addCommentContainer });

  const pickerEl = document.getElementById('interactiveRatingPicker');
  const displayValEl = document.getElementById('ratingDisplayValue');

  function updateStars(val) {
    const starItems = pickerEl.querySelectorAll('.star-picker-item');
    starItems.forEach(item => {
      const idx = parseInt(item.getAttribute('data-star'), 10);
      const clip = item.querySelector('.star-clip');
      if (val >= idx) {
        clip.style.width = '100%';
      } else if (val >= idx - 0.5) {
        clip.style.width = '50%';
      } else {
        clip.style.width = '0%';
      }
    });
    displayValEl.textContent = `${val.toFixed(1)} / 5`;
  }

  pickerEl.querySelectorAll('.star-picker-item').forEach(item => {
    const starNum = parseInt(item.getAttribute('data-star'), 10);

    item.addEventListener('mousemove', (e) => {
      const rect = item.getBoundingClientRect();
      const isLeft = (e.clientX - rect.left) < (rect.width / 2);
      const hoverRating = isLeft ? starNum - 0.5 : starNum;
      updateStars(Math.max(1.0, hoverRating));
    });

    item.addEventListener('click', (e) => {
      const rect = item.getBoundingClientRect();
      const isLeft = (e.clientX - rect.left) < (rect.width / 2);
      currentPickerRating = Math.max(1.0, isLeft ? starNum - 0.5 : starNum);
      updateStars(currentPickerRating);
    });
  });

  pickerEl.addEventListener('mouseleave', () => {
    updateStars(currentPickerRating);
  });

  // Submit comment
  document.getElementById('submitCommentBtn')?.addEventListener('click', async () => {
    const textInput = document.getElementById('commentTextInput');
    const errorEl = document.getElementById('commentErrorMsg');
    const text = textInput.value.trim();

    if (!text) {
      errorEl.textContent = 'Пожалуйста, напишите текст отзыва';
      errorEl.classList.remove('hidden');
      return;
    }
    errorEl.classList.add('hidden');

    try {
      const res = await apiRequest(`/recipes/${recipeId}/comments`, {
        method: 'POST',
        body: JSON.stringify({
          rating: currentPickerRating,
          text,
        }),
      });

      if (res.ok) {
        showToast('Ваш отзыв опубликован!', 'success');
        await loadRecipeComments(recipeId);
        const refRes = await apiRequest(`/recipes/${recipeId}`);
        if (refRes.ok) {
          const updatedRecipe = await refRes.json();
          updateModalRatingSummary(updatedRecipe.rating, updatedRecipe.ratings_count);
          const cardTarget = state.recipes.find(r => r.id === recipeId);
          if (cardTarget) {
            cardTarget.rating = updatedRecipe.rating;
            cardTarget.ratings_count = updatedRecipe.ratings_count;
            renderRecipesGrid(state.recipes);
          }
        }
        renderAddCommentBox(recipeId);
      } else {
        const err = await res.json();
        errorEl.textContent = err.detail || 'Не удалось сохранить отзыв';
        errorEl.classList.remove('hidden');
      }
    } catch (err) {
      errorEl.textContent = 'Ошибка соединения';
      errorEl.classList.remove('hidden');
    }
  });
}

async function loadRecipeComments(recipeId) {
  try {
    const res = await apiRequest(`/recipes/${recipeId}/comments`);
    if (res.ok) {
      const comments = await res.json();
      elements.detailCommentsCountBadge.textContent = comments.length;

      if (comments.length === 0) {
        elements.detailCommentsList.innerHTML = `
          <p class="text-xs text-stone-400 font-light italic py-3 text-center">
            Отзывов пока нет. Приготовьте блюдо и станьте первым, кто оценит этот рецепт!
          </p>
        `;
        return;
      }

      elements.detailCommentsList.innerHTML = comments
        .map(c => {
          const isMyComment = Boolean(state.currentUser && state.currentUser.id === c.user_id);
          const isAdmin = state.currentUser?.role === 'admin';
          const canDelete = isMyComment || isAdmin;

          return `
            <div class="comment-card p-4 rounded-2xl bg-white border border-stone-200/80 shadow-sm space-y-2.5" data-comment-id="${c.id}">
              <div class="flex items-center justify-between gap-2">
                <div class="flex items-center gap-2.5">
                  <div class="w-8 h-8 rounded-full bg-brand-100 text-brand-800 font-bold text-xs flex items-center justify-center uppercase shadow-inner">
                    ${c.username ? c.username.charAt(0) : 'U'}
                  </div>
                  <div>
                    <div class="text-xs font-semibold text-stone-900 flex items-center gap-1.5">
                      <span>${c.username}</span>
                      ${isMyComment ? '<span class="text-[10px] text-brand-700 bg-brand-50 px-1.5 py-0.2 rounded font-bold border border-brand-200/80">Вы</span>' : ''}
                    </div>
                    <div class="text-[10px] text-stone-400 font-light">${formatCommentDate(c.created_at)}</div>
                  </div>
                </div>

                <div class="flex items-center gap-3">
                  <div class="flex items-center gap-1.5 bg-amber-50 px-2 py-1 rounded-xl border border-amber-200/60 shadow-sm">
                    ${renderStarIcons(c.rating, 'w-3.5 h-3.5')}
                    <span class="text-xs font-bold text-amber-900 font-mono">${c.rating.toFixed(1)}</span>
                  </div>
                  ${canDelete ? `
                    <button class="delete-comment-btn text-stone-400 hover:text-rose-600 p-1.5 rounded-lg hover:bg-rose-50 transition-colors" data-id="${c.id}" title="Удалить отзыв">
                      <i data-lucide="trash-2" class="w-3.5 h-3.5"></i>
                    </button>
                  ` : ''}
                </div>
              </div>

              <p class="text-xs text-stone-700 leading-relaxed font-light pl-10">
                ${escapeHtml(c.text)}
              </p>
            </div>
          `;
        })
        .join('');

      lucide.createIcons({ root: elements.detailCommentsList });

      // Bind delete buttons
      elements.detailCommentsList.querySelectorAll('.delete-comment-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
          const commentId = btn.getAttribute('data-id');
          await handleDeleteRecipeComment(recipeId, commentId);
        });
      });
    }
  } catch (err) {
    console.error('Failed to load comments', err);
  }
}

async function handleDeleteRecipeComment(recipeId, commentId) {
  if (!confirm('Вы уверены, что хотите удалить этот отзыв?')) return;

  try {
    const res = await apiRequest(`/recipes/${recipeId}/comments/${commentId}`, {
      method: 'DELETE',
    });

    if (res.status === 204 || res.ok) {
      showToast('Отзыв удален');
      await loadRecipeComments(recipeId);
      const refRes = await apiRequest(`/recipes/${recipeId}`);
      if (refRes.ok) {
        const updatedRecipe = await refRes.json();
        updateModalRatingSummary(updatedRecipe.rating, updatedRecipe.ratings_count);
        const cardTarget = state.recipes.find(r => r.id === recipeId);
        if (cardTarget) {
          cardTarget.rating = updatedRecipe.rating;
          cardTarget.ratings_count = updatedRecipe.ratings_count;
          renderRecipesGrid(state.recipes);
        }
      }
    } else {
      showToast('Ошибка при удалении отзыва', 'error');
    }
  } catch (err) {
    showToast('Сетевая ошибка', 'error');
  }
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function formatCommentDate(dateStr) {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  return date.toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

// Kitchen Timer
function setupTimer() {
  document.querySelectorAll('.timer-preset-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const sec = parseInt(btn.getAttribute('data-seconds'), 10);
      state.timerSeconds += sec;
      updateTimerDisplay();
    });
  });

  elements.timerToggleBtn.addEventListener('click', () => {
    if (state.timerRunning) {
      pauseTimer();
    } else {
      startTimer();
    }
  });

  elements.timerResetBtn.addEventListener('click', () => {
    pauseTimer();
    state.timerSeconds = 0;
    updateTimerDisplay();
  });
}

function startTimer() {
  if (state.timerSeconds <= 0) return;
  state.timerRunning = true;
  elements.timerToggleBtn.textContent = 'Пауза';
  elements.timerToggleBtn.className = 'px-4 py-1.5 bg-amber-800 hover:bg-amber-900 text-white rounded-lg text-xs font-semibold transition-colors';

  state.timerInterval = setInterval(() => {
    if (state.timerSeconds > 0) {
      state.timerSeconds--;
      updateTimerDisplay();
    } else {
      pauseTimer();
      showToast('Время вышло! Проверьте готовность блюда.');
    }
  }, 1000);
}

function pauseTimer() {
  state.timerRunning = false;
  if (state.timerInterval) clearInterval(state.timerInterval);
  elements.timerToggleBtn.textContent = 'Старт';
  elements.timerToggleBtn.className = 'px-4 py-1.5 bg-stone-900 hover:bg-black text-white rounded-lg text-xs font-semibold transition-colors';
}

function updateTimerDisplay() {
  const mins = Math.floor(state.timerSeconds / 60);
  const secs = state.timerSeconds % 60;
  elements.timerDisplay.textContent = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
}

// --- Image File Upload Functions ---

function resetImageUpload() {
  if (elements.recipeFileInput) elements.recipeFileInput.value = '';
  if (elements.formRecipeImage) elements.formRecipeImage.value = '';
  if (elements.formRecipeExternalUrl) elements.formRecipeExternalUrl.value = '';
  if (elements.externalUrlBox) elements.externalUrlBox.classList.add('hidden');

  elements.dropzoneEmptyContent?.classList.remove('hidden');
  elements.dropzoneLoadingContent?.classList.add('hidden');
  elements.dropzonePreviewContent?.classList.add('hidden');
  elements.dropzonePreviewContent?.classList.remove('flex');
}

async function handleFileUpload(file) {
  if (!file) return;

  // Client validation
  if (file.size > 5 * 1024 * 1024) {
    showToast('Размер файла превышает лимит 5 МБ', 'error');
    return;
  }

  const validTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/gif'];
  if (!validTypes.includes(file.type)) {
    showToast('Разрешены только форматы JPEG, PNG, WebP или GIF', 'error');
    return;
  }

  // Show loading spinner
  elements.dropzoneEmptyContent.classList.add('hidden');
  elements.dropzonePreviewContent.classList.add('hidden');
  elements.dropzonePreviewContent.classList.remove('flex');
  elements.dropzoneLoadingContent.classList.remove('hidden');

  const formData = new FormData();
  formData.append('file', file);

  try {
    const headers = {};
    if (state.token) {
      headers['Authorization'] = `Bearer ${state.token}`;
    }

    const response = await fetch(`${API_BASE}/upload/image`, {
      method: 'POST',
      headers,
      body: formData,
    });

    if (response.ok) {
      const data = await response.json();
      elements.formRecipeImage.value = data.url;

      elements.uploadPreviewImg.src = data.url;
      elements.uploadPreviewFilename.textContent = file.name;
      elements.uploadPreviewSize.textContent = `${(file.size / 1024).toFixed(1)} КБ • сохранен на сервере`;

      elements.dropzoneLoadingContent.classList.add('hidden');
      elements.dropzonePreviewContent.classList.remove('hidden');
      elements.dropzonePreviewContent.classList.add('flex');

      showToast('Фотография успешно сохранена на сервере', 'success');
      lucide.createIcons({ root: elements.dropzonePreviewContent });
    } else {
      const err = await response.json();
      showToast(err.detail || 'Ошибка при загрузке файла', 'error');
      resetImageUpload();
    }
  } catch (err) {
    showToast('Сетевая ошибка при загрузке фото', 'error');
    resetImageUpload();
  }
}

// Create Recipe Modal & Dynamic Inputs (All Registered Users)
function openCreateModal() {
  if (!state.currentUser) {
    openAuthModal('login');
    showToast('Войдите в аккаунт, чтобы добавить рецепт');
    return;
  }

  elements.createRecipeForm.reset();
  resetImageUpload();
  elements.formErrorMessage.classList.add('hidden');
  elements.ingredientsRowsContainer.innerHTML = '';
  elements.stepsRowsContainer.innerHTML = '';

  addIngredientRow();
  addIngredientRow();
  addIngredientRow();

  addStepRow();
  addStepRow();

  populateFormCategorySelects();
  handleCategorySelectChange();
  handleSubcategorySelectChange();

  elements.recipeCreateModal.classList.remove('hidden');
  lucide.createIcons({ root: elements.recipeCreateModal });
}

function closeCreateModal() {
  elements.recipeCreateModal.classList.add('hidden');
}

function handleCategorySelectChange() {
  if (elements.formRecipeCategorySelect.value === '__custom__') {
    elements.formRecipeCategoryCustom.classList.remove('hidden');
    elements.formRecipeCategoryCustom.focus();
  } else {
    elements.formRecipeCategoryCustom.classList.add('hidden');
  }
}

function handleSubcategorySelectChange() {
  if (elements.formRecipeSubcatSelect.value === '__custom__') {
    elements.formRecipeSubcatCustom.classList.remove('hidden');
    elements.formRecipeSubcatCustom.focus();
  } else {
    elements.formRecipeSubcatCustom.classList.add('hidden');
  }
}

function addIngredientRow(name = '', qty = '', unit = 'г') {
  const row = document.createElement('div');
  row.className = 'flex items-center gap-2 ingredient-row';
  row.innerHTML = `
    <input type="text" placeholder="Ингредиент" value="${name}" required class="ing-name flex-1 px-3 py-2 text-xs bg-stone-50 border border-stone-200 rounded-xl outline-none focus:border-stone-900" />
    <input type="number" step="any" placeholder="Кол-во" value="${qty}" required class="ing-qty w-20 px-3 py-2 text-xs bg-stone-50 border border-stone-200 rounded-xl outline-none focus:border-stone-900" />
    <input type="text" placeholder="Ед. (г, мл)" value="${unit}" required class="ing-unit w-20 px-3 py-2 text-xs bg-stone-50 border border-stone-200 rounded-xl outline-none focus:border-stone-900" />
    <button type="button" class="remove-row-btn text-stone-400 hover:text-stone-700 p-1.5 rounded-lg transition-colors">
      <i data-lucide="x" class="w-4 h-4"></i>
    </button>
  `;
  row.querySelector('.remove-row-btn').addEventListener('click', () => {
    if (elements.ingredientsRowsContainer.children.length > 1) {
      row.remove();
    } else {
      showToast('Должен оставаться хотя бы один ингредиент');
    }
  });
  elements.ingredientsRowsContainer.appendChild(row);
  lucide.createIcons({ root: row });
}

function addStepRow(text = '') {
  const currentCount = elements.stepsRowsContainer.children.length + 1;
  const row = document.createElement('div');
  row.className = 'flex items-start gap-2.5 step-row';
  row.innerHTML = `
    <span class="step-badge mt-2 w-5 h-5 rounded-full bg-stone-200 text-stone-700 text-[11px] font-bold flex items-center justify-center flex-shrink-0">
      ${currentCount}
    </span>
    <textarea rows="2" placeholder="Опишите шаг приготовления..." required class="step-text flex-1 px-3.5 py-2 text-xs bg-stone-50 border border-stone-200 rounded-xl outline-none focus:border-stone-900 resize-none">${text}</textarea>
    <button type="button" class="remove-row-btn mt-2 text-stone-400 hover:text-stone-700 p-1 rounded-lg transition-colors">
      <i data-lucide="x" class="w-4 h-4"></i>
    </button>
  `;
  row.querySelector('.remove-row-btn').addEventListener('click', () => {
    if (elements.stepsRowsContainer.children.length > 1) {
      row.remove();
      renumberSteps();
    } else {
      showToast('Должен оставаться хотя бы один шаг');
    }
  });
  elements.stepsRowsContainer.appendChild(row);
  lucide.createIcons({ root: row });
}

function renumberSteps() {
  const rows = elements.stepsRowsContainer.querySelectorAll('.step-row');
  rows.forEach((r, idx) => {
    const badge = r.querySelector('.step-badge');
    if (badge) badge.textContent = idx + 1;
  });
}

// Submit Create Recipe (All Registered Users)
async function handleCreateRecipeSubmit(e) {
  e.preventDefault();
  elements.formErrorMessage.classList.add('hidden');

  if (!state.currentUser) {
    showFormError('Войдите в систему, чтобы опубликовать рецепт.');
    return;
  }

  const name = document.getElementById('formRecipeName').value.trim();
  const description = document.getElementById('formRecipeDescription').value.trim();
  let image_path = elements.formRecipeImage?.value.trim() || '';
  if (!image_path && elements.formRecipeExternalUrl?.value.trim()) {
    image_path = elements.formRecipeExternalUrl.value.trim();
  }

  let category = elements.formRecipeCategorySelect.value;
  if (category === '__custom__') {
    category = elements.formRecipeCategoryCustom.value.trim();
  }
  if (!category) {
    showFormError('Укажите категорию рецепта');
    return;
  }

  let subcategory = elements.formRecipeSubcatSelect.value;
  if (subcategory === '__custom__') {
    subcategory = elements.formRecipeSubcatCustom.value.trim();
  }
  if (subcategory === '') subcategory = null;

  const ingredients = [];
  const ingRows = elements.ingredientsRowsContainer.querySelectorAll('.ingredient-row');
  for (const row of ingRows) {
    const ingName = row.querySelector('.ing-name').value.trim();
    const ingQty = parseFloat(row.querySelector('.ing-qty').value);
    const ingUnit = row.querySelector('.ing-unit').value.trim();

    if (ingName) {
      ingredients.push({
        name: ingName,
        unit: ingUnit ? { name: ingUnit, quantity: isNaN(ingQty) || ingQty <= 0 ? 1 : ingQty } : null,
      });
    }
  }

  const steps = [];
  const stepRows = elements.stepsRowsContainer.querySelectorAll('.step-row');
  let stepIndex = 1;
  for (const row of stepRows) {
    const stepText = row.querySelector('.step-text').value.trim();
    if (stepText) {
      steps.push({
        number: stepIndex++,
        text: stepText,
      });
    }
  }

  const payload = {
    name,
    description,
    category,
    subcategory,
    image_path: image_path || null,
    ingredients,
    steps,
  };

  try {
    const res = await apiRequest('/recipes', {
      method: 'POST',
      body: JSON.stringify(payload),
    });

    if (res.ok) {
      const created = await res.json();
      showToast(`Рецепт «${created.name}» опубликован`, 'success');
      closeCreateModal();
      await loadCategories();
      await loadRecipes();
      openRecipeDetail(created.id);
    } else {
      const err = await res.json();
      showFormError(err.detail || 'Ошибка при сохранении рецепта');
    }
  } catch (err) {
    showFormError('Ошибка при отправке запроса');
  }
}

function showFormError(msg) {
  elements.formErrorMessage.textContent = msg;
  elements.formErrorMessage.classList.remove('hidden');
}

// Auth Modal
let authMode = 'login';

function openAuthModal(mode = 'login') {
  authMode = mode;
  elements.authErrorMsg.classList.add('hidden');
  elements.authForm.reset();
  updateAuthModalUI();
  elements.authModal.classList.remove('hidden');
  elements.authUsername.focus();
}

function closeAuthModal() {
  elements.authModal.classList.add('hidden');
}

function updateAuthModalUI() {
  if (authMode === 'login') {
    elements.authModalTitle.textContent = 'Вход в аккаунт';
    elements.authSubmitBtn.textContent = 'Войти';
    elements.authTabLogin.className = 'flex-1 py-1.5 rounded-lg bg-white text-stone-900 shadow-sm transition-all';
    elements.authTabRegister.className = 'flex-1 py-1.5 rounded-lg text-stone-500 hover:text-stone-900 transition-all';
  } else {
    elements.authModalTitle.textContent = 'Создание аккаунта';
    elements.authSubmitBtn.textContent = 'Зарегистрироваться';
    elements.authTabRegister.className = 'flex-1 py-1.5 rounded-lg bg-white text-stone-900 shadow-sm transition-all';
    elements.authTabLogin.className = 'flex-1 py-1.5 rounded-lg text-stone-500 hover:text-stone-900 transition-all';
  }
}

async function handleAuthSubmit(e) {
  e.preventDefault();
  elements.authErrorMsg.classList.add('hidden');

  const username = elements.authUsername.value.trim();
  const password = elements.authPassword.value;

  try {
    if (authMode === 'register') {
      const regRes = await fetch(`${API_BASE}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password, role: 'user' }),
      });

      if (!regRes.ok) {
        const err = await regRes.json();
        elements.authErrorMsg.textContent = err.detail || 'Ошибка регистрации';
        elements.authErrorMsg.classList.remove('hidden');
        return;
      }
    }

    const loginRes = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });

    if (loginRes.ok) {
      const data = await loginRes.json();
      state.token = data.access_token;
      localStorage.setItem('access_token', state.token);
      await checkAuth();
      closeAuthModal();
      showToast(`Вы вошли как ${username}`, 'success');
      loadRecipes();
    } else {
      const err = await loginRes.json();
      elements.authErrorMsg.textContent = err.detail || 'Неверные данные';
      elements.authErrorMsg.classList.remove('hidden');
    }
  } catch (err) {
    elements.authErrorMsg.textContent = 'Сетевая ошибка';
    elements.authErrorMsg.classList.remove('hidden');
  }
}

// Event Listeners
function initEventListeners() {
  let searchTimeout;
  const onSearch = (value) => {
    state.searchQuery = value.trim();
    if (state.searchQuery) {
      elements.clearSearchBtn?.classList.remove('hidden');
    } else {
      elements.clearSearchBtn?.classList.add('hidden');
    }
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(loadRecipes, 250);
  };

  elements.searchInput?.addEventListener('input', (e) => onSearch(e.target.value));
  elements.searchInputMobile?.addEventListener('input', (e) => onSearch(e.target.value));

  elements.clearSearchBtn?.addEventListener('click', () => {
    elements.searchInput.value = '';
    if (elements.searchInputMobile) elements.searchInputMobile.value = '';
    state.searchQuery = '';
    elements.clearSearchBtn.classList.add('hidden');
    loadRecipes();
  });

  elements.viewAllBtn.addEventListener('click', () => {
    state.viewOnlyFav = false;
    elements.viewAllBtn.className = 'filter-tab active font-semibold text-brand-700 border-b-2 border-brand-600 pb-1';
    elements.viewFavBtn.className = 'filter-tab text-stone-500 hover:text-brand-700 pb-1';
    loadRecipes();
  });

  elements.viewFavBtn.addEventListener('click', () => {
    if (!state.currentUser) {
      openAuthModal('login');
      showToast('Войдите, чтобы просматривать избранное');
      return;
    }
    state.viewOnlyFav = true;
    elements.viewFavBtn.className = 'filter-tab active font-semibold text-brand-700 border-b-2 border-brand-600 pb-1';
    elements.viewAllBtn.className = 'filter-tab text-stone-500 hover:text-brand-700 pb-1';
    loadRecipes();
  });

  elements.favoritesTabBtn.addEventListener('click', () => {
    elements.viewFavBtn.click();
  });

  elements.resetFiltersBtn.addEventListener('click', () => {
    state.activeCategory = '';
    state.activeSubcategory = '';
    state.searchQuery = '';
    state.viewOnlyFav = false;
    if (elements.searchInput) elements.searchInput.value = '';
    if (elements.searchInputMobile) elements.searchInputMobile.value = '';
    elements.clearSearchBtn?.classList.add('hidden');
    renderFilterControls();
    elements.viewAllBtn.click();
  });

  elements.closeDetailModalBtn.addEventListener('click', closeRecipeDetail);
  elements.closeDetailModalFooterBtn.addEventListener('click', closeRecipeDetail);
  elements.recipeDetailModal.addEventListener('click', (e) => {
    if (e.target === elements.recipeDetailModal) closeRecipeDetail();
  });

  elements.openCreateModalBtn.addEventListener('click', openCreateModal);
  elements.closeCreateModalBtn.addEventListener('click', closeCreateModal);
  elements.cancelCreateModalBtn.addEventListener('click', closeCreateModal);
  elements.recipeCreateModal.addEventListener('click', (e) => {
    if (e.target === elements.recipeCreateModal) closeCreateModal();
  });

  elements.formRecipeCategorySelect.addEventListener('change', handleCategorySelectChange);
  elements.formRecipeSubcatSelect.addEventListener('change', handleSubcategorySelectChange);
  elements.addIngredientRowBtn.addEventListener('click', () => addIngredientRow());
  elements.addStepRowBtn.addEventListener('click', () => addStepRow());
  elements.createRecipeForm.addEventListener('submit', handleCreateRecipeSubmit);

  // Image Upload Dropzone Listeners
  if (elements.imageDropzone) {
    elements.imageDropzone.addEventListener('click', (e) => {
      if (!e.target.closest('#removeUploadedFileBtn')) {
        elements.recipeFileInput?.click();
      }
    });

    elements.recipeFileInput?.addEventListener('change', (e) => {
      if (e.target.files && e.target.files[0]) {
        handleFileUpload(e.target.files[0]);
      }
    });

    elements.imageDropzone.addEventListener('dragover', (e) => {
      e.preventDefault();
      elements.imageDropzone.classList.add('dragover');
    });

    elements.imageDropzone.addEventListener('dragleave', () => {
      elements.imageDropzone.classList.remove('dragover');
    });

    elements.imageDropzone.addEventListener('drop', (e) => {
      e.preventDefault();
      elements.imageDropzone.classList.remove('dragover');
      if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files[0]) {
        handleFileUpload(e.dataTransfer.files[0]);
      }
    });

    elements.removeUploadedFileBtn?.addEventListener('click', (e) => {
      e.stopPropagation();
      resetImageUpload();
    });

    elements.toggleExternalUrlBtn?.addEventListener('click', () => {
      elements.externalUrlBox?.classList.toggle('hidden');
    });

    elements.formRecipeExternalUrl?.addEventListener('input', (e) => {
      if (e.target.value.trim()) {
        elements.formRecipeImage.value = e.target.value.trim();
      }
    });
  }

  elements.closeAuthModalBtn.addEventListener('click', closeAuthModal);
  elements.authModal.addEventListener('click', (e) => {
    if (e.target === elements.authModal) closeAuthModal();
  });
  elements.authTabLogin.addEventListener('click', () => {
    authMode = 'login';
    updateAuthModalUI();
  });
  elements.authTabRegister.addEventListener('click', () => {
    authMode = 'register';
    updateAuthModalUI();
  });
  elements.authForm.addEventListener('submit', handleAuthSubmit);

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      closeRecipeDetail();
      closeCreateModal();
      closeAuthModal();
    }
  });

  setupTimer();
}

async function initApp() {
  initEventListeners();
  lucide.createIcons();
  await checkAuth();
  await loadCategories();
  await loadRecipes();
}

window.addEventListener('DOMContentLoaded', initApp);
