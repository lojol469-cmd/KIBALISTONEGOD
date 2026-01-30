const express = require('express');
const nodemailer = require('nodemailer');
const crypto = require('crypto');
const cors = require('cors');
const cloudinary = require('cloudinary').v2;
require('dotenv').config();

console.log('Environment variables loaded. CLOUDINARY_CLOUD_NAME:', process.env.CLOUDINARY_CLOUD_NAME);

const app = express();
app.use(express.json());
app.use(cors());

// Configuration Cloudinary
cloudinary.config({
  cloud_name: process.env.CLOUDINARY_CLOUD_NAME,
  api_key: process.env.CLOUDINARY_API_KEY,
  api_secret: process.env.CLOUDINARY_API_SECRET
});

console.log('Cloudinary configured with cloud_name:', process.env.CLOUDINARY_CLOUD_NAME);

// Configuration Nodemailer
const transporter = nodemailer.createTransport({
  service: 'gmail',
  auth: {
    user: process.env.EMAIL_USER,
    pass: process.env.EMAIL_PASS
  }
});

console.log('Nodemailer transporter created for user:', process.env.EMAIL_USER);

// Stockage temporaire des OTP
const otpStore = new Map();

// Fonction pour charger les utilisateurs depuis Cloudinary
async function loadUsers() {
  try {
    console.log('Loading users from Cloudinary...');
    const result = await cloudinary.api.resources({ type: 'upload', prefix: 'users/', max_results: 500 });
    console.log('Cloudinary resources fetched:', result.resources.length);
    const users = {};
    for (const resource of result.resources) {
      const publicId = resource.public_id;
      const email = publicId.replace('users/', '');
      console.log('Processing user:', email);
      const downloadResult = await cloudinary.api.resource(publicId);
      const userData = JSON.parse(Buffer.from(downloadResult.secure_url.split(',')[1], 'base64').toString());
      users[email] = userData;
    }
    console.log('Users loaded:', Object.keys(users).length);
    return users;
  } catch (error) {
    console.error('Erreur chargement utilisateurs:', error);
    return {};
  }
}

// Fonction pour sauvegarder un utilisateur dans Cloudinary
async function saveUser(email, userData) {
  try {
    const dataStr = JSON.stringify(userData);
    const dataBase64 = Buffer.from(dataStr).toString('base64');
    await cloudinary.uploader.upload(`data:text/plain;base64,${dataBase64}`, {
      public_id: `users/${email}`,
      resource_type: 'raw'
    });
  } catch (error) {
    console.error('Erreur sauvegarde utilisateur:', error);
  }
}

let users = {};

// Charger les utilisateurs au démarrage
loadUsers().then(loadedUsers => {
  users = loadedUsers;
});

// Route d'inscription
app.post('/register', async (req, res) => {
  const { email } = req.body;

  if (!email) {
    return res.status(400).json({ error: 'Email requis' });
  }

  if (users[email]) {
    return res.status(400).json({ error: 'Utilisateur déjà enregistré' });
  }

  const otp = crypto.randomInt(100000, 999999).toString();

  otpStore.set(email, { otp, expires: Date.now() + 5 * 60 * 1000 });

  try {
    console.log('Sending OTP email to:', email);
    await transporter.sendMail({
      from: process.env.EMAIL_USER,
      to: email,
      subject: 'Code de vérification - Inscription',
      text: `Votre code de vérification est: ${otp}`
    });
    console.log('OTP email sent successfully');
    res.json({ message: 'Code envoyé à votre email' });
  } catch (error) {
    console.error('Erreur envoi email:', error);
    res.status(500).json({ error: 'Erreur envoi email' });
  }
});

// Route de connexion
app.post('/login', async (req, res) => {
  const { email } = req.body;

  if (!email) {
    return res.status(400).json({ error: 'Email requis' });
  }

  if (!users[email]) {
    return res.status(400).json({ error: 'Utilisateur non trouvé' });
  }

  const otp = crypto.randomInt(100000, 999999).toString();

  otpStore.set(email, { otp, expires: Date.now() + 5 * 60 * 1000 });

  try {
    console.log('Sending login OTP email to:', email);
    await transporter.sendMail({
      from: process.env.EMAIL_USER,
      to: email,
      subject: 'Code de vérification - Connexion',
      text: `Votre code de vérification est: ${otp}`
    });
    console.log('Login OTP email sent successfully');
    res.json({ message: 'Code envoyé à votre email' });
  } catch (error) {
    console.error('Erreur envoi email:', error);
    res.status(500).json({ error: 'Erreur envoi email' });
  }
});

// Route de vérification OTP
app.post('/verify', async (req, res) => {
  const { email, otp } = req.body;

  if (!email || !otp) {
    return res.status(400).json({ error: 'Email et OTP requis' });
  }

  const stored = otpStore.get(email);

  if (!stored || stored.otp !== otp || Date.now() > stored.expires) {
    return res.status(400).json({ error: 'OTP invalide ou expiré' });
  }

  otpStore.delete(email);

  // Enregistrer l'utilisateur si c'est une inscription
  if (!users[email]) {
    users[email] = { email, registeredAt: new Date() };
    await saveUser(email, users[email]);
  }

  res.json({ message: 'Authentification réussie', token: 'dummy-token' });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Serveur démarré sur le port ${PORT}`);
});