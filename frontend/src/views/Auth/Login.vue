<template>
  <AuthForm
    title="Login"
    imageSrc="../assets/images/login.png"
    imageAlt="Login Image"
    :fields="loginFields"
    buttonText="Log in"
    linkText="Not a User?"
    linkActionText="Sign Up"
    linkUrl="/signup"
    :handleSubmit="login"
    :errorMessage="errorMessage"
  />
</template>

<script>
import AuthForm from '@/components/AuthForm.vue'
import axios from 'axios'

export default {
  components: {
    AuthForm
  },
  data() {
    return {
      errorMessage: '' // State to hold the error message
    }
  },
  computed: {
    loginFields() {
      return [
        {
          type: 'text',
          name: 'email',
          placeholder: 'Email',
        },
        {
          type: 'password',
          name: 'password',
          placeholder: 'Password',
        }
      ]
    }
  },
  methods: {
    login(formData) {
      this.errorMessage = '' // Reset error message before each request
      axios
        .post('http://127.0.0.1:5000/login', {
          email: formData.email,
          password: formData.password
        })
        .then((response) => {
          localStorage.setItem('authToken', response.data.access_token)
          console.log('Login successful:', response.data.access_token)
          this.$router.push('/') // Navigate to the protected route
        })
        .catch((error) => {
          console.error('Login error:', error)
          this.errorMessage = 'Invalid username or password' // Set error message
        })
    }
  }
}
</script>
