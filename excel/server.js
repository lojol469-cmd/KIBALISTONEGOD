const express = require('express');
const nodemailer = require('nodemailer');
const crypto = require('crypto');
const cors = require('cors');
const https = require('https');
const cloudinary = require('cloudinary').v2;
require('dotenv').config({ path: __dirname + '/.env' });

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
    const result = await cloudinary.api.resources({ resource_type: 'raw', type: 'upload', prefix: 'users/', max_results: 500 });
    console.log('Cloudinary resources fetched:', result.resources.length);
    const users = {};
    for (const resource of result.resources) {
      const publicId = resource.public_id;
      console.log('Processing user:', publicId);
      const downloadResult = await cloudinary.api.resource(publicId, { resource_type: 'raw' });
      const url = downloadResult.secure_url;
      const userData = await new Promise((resolve, reject) => {
        https.get(url, (res) => {
          let data = '';
          res.on('data', (chunk) => data += chunk);
          res.on('end', () => {
            try {
              resolve(JSON.parse(data));
            } catch (e) {
              reject(e);
            }
          });
        }).on('error', reject);
      });
      if (userData.email) {
        users[userData.email] = userData;
      }
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
    const hash = crypto.createHash('md5').update(email).digest('hex');
    const dataStr = JSON.stringify({ ...userData, email }); // Assurer que l'email est inclus
    const dataBase64 = Buffer.from(dataStr).toString('base64');
    await cloudinary.uploader.upload(`data:text/plain;base64,${dataBase64}`, {
      public_id: `users/${hash}`,
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
    console.log(`Tentative d'inscription pour email déjà enregistré: ${email}`);
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
    console.log('OTP email sent successfully for registration');
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
    console.log(`Tentative de connexion pour email non enregistré: ${email}`);
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
    console.log(`OTP invalide ou expiré pour ${email}`);
    return res.status(400).json({ error: 'OTP invalide ou expiré' });
  }

  otpStore.delete(email);

  // Enregistrer l'utilisateur si c'est une inscription
  if (!users[email]) {
    users[email] = { email, registeredAt: new Date() };
    console.log(`Nouveau utilisateur enregistré: ${email}`);
    await saveUser(email, users[email]);
    console.log(`Utilisateur ${email} sauvegardé dans Cloudinary`);
  } else {
    console.log(`Utilisateur existant connecté: ${email}`);
  }

  res.json({ message: 'Authentification réussie', token: 'dummy-token' });
});

// Route pour envoyer des notifications par email
app.post('/send-notification', async (req, res) => {
  try {
    const { to, subject, html, action_type, entity_type, entity_id, user_info, timestamp } = req.body;

    if (!to || !subject || !html) {
      return res.status(400).json({ error: 'Destinataire, sujet et contenu HTML requis' });
    }

    // Configuration de l'email
    const mailOptions = {
      from: process.env.EMAIL_USER,
      to: to,
      subject: subject,
      html: html
    };

    // Envoi de l'email
    const info = await transporter.sendMail(mailOptions);
    console.log('Email de notification envoyé:', info.messageId);

    res.json({ 
      message: 'Notification envoyée avec succès',
      messageId: info.messageId,
      action_type,
      entity_type,
      entity_id,
      user_info,
      timestamp
    });

  } catch (error) {
    console.error('Erreur envoi notification:', error);
    res.status(500).json({ error: 'Erreur envoi notification: ' + error.message });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Serveur démarré sur le port ${PORT}`);
});