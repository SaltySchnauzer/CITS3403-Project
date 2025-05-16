document.addEventListener('DOMContentLoaded', function() {
  const input = document.getElementById('friend-search-input');
  const results = document.getElementById('search-results');

  input.addEventListener('keyup', function() {
    const q = input.value.trim();
    if (q.length < 2) {
      results.innerHTML = '';
      return;
    }
    fetch(`/friends/search?q=${encodeURIComponent(q)}`)
      .then(response => response.json())
      .then(users => {
        results.innerHTML = users.map(u => `
          <div class="px-4 py-2 hover:bg-gray-100 cursor-pointer"
               data-id="${u.id}"
          >${u.username}</div>
        `).join('');

        results.querySelectorAll('div[data-id]').forEach(el => {
          el.addEventListener('click', function() {
            const userId = el.getAttribute('data-id');
            fetch('/friends/add', {
              method: 'POST',
              headers: {'Content-Type': 'application/json'},
              body: JSON.stringify({user_id: userId})
            })
            .then(r => r.json())
            .then(data => {
              if (data.success) {
                alert(
                  `${data.username} added as a friend.\n` +
                  `They must add you back before you can see their data.`
                );
                input.value = '';
                results.innerHTML = '';
              }
            });
          });
        });
      });
  });
});