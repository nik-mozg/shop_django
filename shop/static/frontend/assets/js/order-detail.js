var mix = {
	methods: {
		
		getOrder(orderId) {
			if (typeof orderId !== 'number' || isNaN(orderId) || orderId <= 0) {
				return;
			}			
			this.getData(`/api/orders/${orderId}/`)
				.then(data => {					
					if (data) {
						this.orderId = data.id || null;
						this.createdAt = data.createdAt || null;
						this.fullName = data.fullName || '';
						this.phone = data.phone || '';
						this.email = data.email || '';
						this.deliveryType = data.deliveryType || '';
						this.city = data.city || '';
						this.address = data.address || '';
						this.paymentType = data.paymentType || '';
						this.status = data.status || '';
						this.totalCost = data.totalCost || 0;
						this.products = data.products || [];						
						if (typeof data.paymentError !== 'undefined') {
							this.paymentError = data.paymentError;
						}
					} else {
						console.error('No data received for the order.');
					}
				})
				.catch(err => {
					console.error('Error fetching order:', err);  // Логирование ошибок
				});
		},

		// Подтверждение заказа
		confirmOrder() {
			
			if (this.orderId !== null) {
				this.postData(`/api/orders/${this.orderId}/`, { ...this })
					.then(({ data: { orderId } }) => {
						alert('Заказ подтвержден! Переход на страницу оплаты!');
						location.replace(`/api/create-payment/${orderId}/`);
						//location.replace(`/payment/${orderId}/`);
					})
					.catch(err => {
						console.warn('Ошибка при подтверждения заказа:', err);  
					});
			} else {
				console.warn('No orderId to confirm.');
			}
		},

		auth() {
			const username = document.querySelector('#username').value;
			const password = document.querySelector('#password').value;
			console.log(`Attempting to authenticate user: ${username}`);  
			this.postData('/api/sign-in/', JSON.stringify({ username, password }))
				.then(({ data, status }) => {					
					location.assign(`/orders/${this.orderId}`);
				})
				.catch(err => {
					alert('Ошибка авторизации');
				});
		}
	},

	// Монтирование компонента
	mounted() {
		// Проверка URL и извлечение orderId
		if(location.pathname.startsWith('/orders/')) {
			const orderId = location.pathname.replace('/orders/', '').replace('/', '');
			this.orderId = orderId.length ? Number(orderId) : null;
			
			// Логирование и проверка на валидность orderId
			if (this.orderId && this.orderId > 0) {
				this.getOrder(this.orderId);
			} else {
				console.warn('Invalid orderId extracted from path:', orderId);  // Логирование ошибки
			}
		}
	},

	// Данные компонента
	data() {
		return {
			orderId: null,
			createdAt: null,
			fullName: null,
			phone: null,
			email: null,
			deliveryType: null,
			city: null,
			address: null,
			paymentType: null,
			status: null,
			totalCost: null,
			products: [],
			paymentError: null,
		}
	},
}
