const validateUsername = (username) => {
    const errors = {};
    if (!username) {
        errors.username = "Username is required";
    } else if (username.length < 4) {
        errors.username = "Username must be at least 4 characters long";
    } else if (username.length > 20) {
        errors.username = "Username must be at most 20 characters long";
    } else if (!/^[a-zA-Z0-9]+$/.test(username)) {
        errors.username = "Username must contain only alphanumeric characters";
    }
    return errors;
}

const validatePassword = (password) => {
    const errors = {};
    if (!password) {
        errors.password = "Password is required";
    } else if (password.length < 6) {
        errors.password = "Password must be at least 6 characters long";
    } else if (password.length > 40) {
        errors.password = "Password must be at most 40 characters long";
    } else if (!/^[a-zA-Z0-9]+$/.test(password)) {
        errors.password = "Password must contain only alphanumeric characters";
    }
    return errors;
}

const validateEmail = (email) => {
    const errors = {};
    if (!email) {
        errors.email = "Email is required";
    } else if (!/\S+@\S+\.\S+/.test(email)) {
        errors.email = "Email address is invalid";
    }
    return errors;
}

const validatePlayername = (playername) => {
    const errors = {};
    if (!playername) {
        errors.playername = "Playername is required";
    } else if (playername.length < 4) {
        errors.playername = "Playername must be at least 4 characters long";
    } else if (playername.length > 20) {
        errors.playername = "Playername must be at most 20 characters long";
    } else if (!/^[a-zA-Z0-9]+$/.test(playername)) {
        errors.playername = "Playername must contain only alphanumeric characters";
    }
    return errors;
}

export { validateUsername, validatePassword, validateEmail, validatePlayername };
