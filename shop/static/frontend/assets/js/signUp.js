var mix = {
	methods: {
		signUp() {
			const name = document.querySelector('#name').value;
			const username = document.querySelector('#login').value;
			const password = document.querySelector('#password').value;

			axios.post('/api/sign-up/', { name, username, password })
				.then(({ data }) => {
					alert(data.message); // Успешная регистрация
					location.assign('/'); // Перенаправление на главную страницу
				})
				.catch((error) => {
					// Если ошибка, показываем сообщение от сервера
					alert(error.response?.data?.error || 'Ошибка регистрации!');
				});
		}
	},
	mounted() {
		console.log('Sign-up component mounted');
	},
	data() {
		return {};
	}
};
