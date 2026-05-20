const express = require('express');
const app = express();

function fetchData(url) {
    return fetch(url).then(r => r.json());
}

class UserService {
    getUser(id) {
        return this.db.find(id);
    }

    createUser(data) {
        return this.db.insert(data);
    }
}

module.exports = { fetchData, UserService };
