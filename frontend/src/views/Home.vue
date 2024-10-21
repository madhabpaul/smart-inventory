<template>




  <div class="hello">
    <div>
      <div class="wrap">
        <h1>Welcome, {{ email }}</h1>
        <hr>
        <h2>Add Items</h2>
        <form @submit="addItems">
          <div class="form-group">
            <input type="hidden" v-model=userid class="form-control">
            <input type="text" v-model="insert_query" class="form-control">
          </div>
          <div class="form-group">
            <button class="btn btn-sm btn-info" type="submit">Add Item</button>
          </div>
        </form>
        <hr>
        <h2>Your Items</h2>
        <tbody>
          <tr v-for="(item, index) in items" :key="index">
            <td class="col-md-3 ">{{ item.item_name }}</td>
            <td class="col-md-3 ">{{ item.unit }}</td>
            <td class="col-md-3 ">{{ item.quantity }}</td>
            <td class="col-md-3 ">
              <button @click="updateItem(item.id)" type="button" class="btn btn-warning me-2 btn-sm">Update</button>
            </td>
            <td class="col-md-3 ">
              <button @click="deleteItem(item.id)" type="button" class="btn btn-danger btn-sm">Delete</button>
            </td>
          </tr>
        </tbody>
        <button class="logout-button" @click="logout">Logout</button>
      </div>
    </div>
  </div>
</template>

<script>
import { jwtDecode } from 'jwt-decode'
import axios from 'axios';

export default {
  name: 'Hello',
  data() {
    return {
      email: '',
      userid: '',
      items: [],
      insert_query: '',
    }
  },
  mounted() {
    const token = localStorage.getItem('authToken')
    const decoded = jwtDecode(token)
    const email = decoded.email
    const userid = decoded.user_id
    this.email = email
    this.userid = userid
    this.getItems(userid)
  },
  methods: {
    logout() {
      localStorage.removeItem('authToken')
      this.$router.push('/login')
    },
    getItems(userid) {
      axios.get('http://127.0.0.1:5000/items/' + userid)
        .then((res) => {
          this.items = res.data;
        })
        .catch((error) => {
          console.error(error);
        });
    },
    addItems() {
      axios.post("http://127.0.0.1:5000/addItems",
        {
          insert_query: this.insert_query,
          userid: this.userid
        }
      ).then(response => {
        console.log(response.message)
        alert('New record Successfully added')
        this.insert_query = ''
      }).catch(err => {
        console.log(err)
      })
    }
  },
}
</script>

<style scoped>
.hello {
  display: -webkit-box;
  display: -webkit-flex;
  display: -moz-box;
  display: -ms-flexbox;
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  width: 100%;
  text-align: center;
  margin: 0px;
  padding: 0px;
  color: #fff;
  font-family: 'Montserrat', sans-serif;
  background: linear-gradient(-145deg, #ee7752, #e73c7e, #23a6d5, #23d5ab, #d5c023, #ecece9);
  background-size: 400% 400%;
  /* -webkit-animation: Gradient 15s ease infinite;
  -moz-animation: Gradient 15s ease infinite;
  animation: Gradient 15s ease infinite; */
}

.wrap h1 {
  font-size: 30px;
  font-weight: 700;
  margin: 1em;
}

.wrap h2 {
  font-size: 24px;
  font-weight: 400;
  line-height: 1.6;
  margin: 1em;
}

.logout-button {
  padding: 16px 32px;
  margin: 4px;
  border: 1px solid #ffffff;
  background: transparent;
  height: 50px;
  width: 100%;
  border-radius: 25px;
  font-family: 'Montserrat', sans-serif;
  font-weight: 700;
  font-size: 15px;
  line-height: 1.5;
  color: #fff;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 0 25px;
  transition: all 0.4s;
}

.logout-button:hover {
  cursor: pointer;
  background: #ffffff;
  color: #626262;
}

.logout-button:focus {
  background: #626262;
  border-color: #626262;
  box-shadow: none;
}

@-webkit-keyframes Gradient {
  0% {
    background-position: 0% 50%;
  }

  50% {
    background-position: 100% 50%;
  }

  100% {
    background-position: 0% 50%;
  }
}

@-moz-keyframes Gradient {
  0% {
    background-position: 0% 50%;
  }

  50% {
    background-position: 100% 50%;
  }

  100% {
    background-position: 0% 50%;
  }
}

@keyframes Gradient {
  0% {
    background-position: 0% 50%;
  }

  50% {
    background-position: 100% 50%;
  }

  100% {
    background-position: 0% 50%;
  }
}
</style>
