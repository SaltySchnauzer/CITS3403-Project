document.addEventListener('DOMContentLoaded', function() {
  const input = document.getElementById('friend-search-input');
  const results = document.getElementById('search-results');
  const toastContainer = document.getElementById('toast-container');

  function showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'flex items-center justify-between bg-white border-l-4 border-orange-500 shadow-lg px-4 py-2 rounded-md mb-2';
    toast.innerHTML = `
      <span class="text-gray-800">${message}</span>
      <button class="ml-4 text-gray-500 hover:text-gray-700">&times;</button>
    `;
    // remove on click
    toast.querySelector('button').addEventListener('click', () => {
      toast.remove();
    });
    toastContainer.appendChild(toast);
    // auto-dismiss
    setTimeout(() => toast.remove(), 4000);
  }

  input.addEventListener('keyup', function() {
    const q = input.value.trim();
    if (q.length < 1) {
      results.innerHTML = '';
      return;
    }
    fetch(`/friends/search?q=${encodeURIComponent(q)}`)
      .then(response => response.json())
      .then(users => {
        results.innerHTML = users.map(u => `
          <div class="flex justify-between items-center px-4 py-2 hover:bg-gray-50 cursor-default">
            <span class="text-gray-800">${u.username}</span>
            <button data-id="${u.id}"
                    class="add-btn bg-orange-500 hover:bg-orange-600 text-white text-sm px-2 py-1 rounded">
              Add
            </button>
          </div>
        `).join('');

        results.querySelectorAll('button.add-btn').forEach(btn => {
          btn.addEventListener('click', function() {
            const userId = btn.getAttribute('data-id');
            fetch('/friends/add', {
              method: 'POST',
              headers: {'Content-Type': 'application/json'},
              body: JSON.stringify({user_id: userId})
            })
            .then(r => r.json())
            .then(data => {
              if (data.error) {
                showToast(data.error);
              } else if (data.success) {
                showToast(`${data.username} added as a friend. They must add you back to share data.`);
                input.value = '';
                results.innerHTML = '';
              }
            });
          });
        });
      });
  });
});
