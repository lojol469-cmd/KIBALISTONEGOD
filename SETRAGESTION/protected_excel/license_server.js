const express = require('express');
const nodemailer = require('nodemailer');
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');
const qrcode = require('qrcode');
require('dotenv').config();

const app = express();
const PORT = 4000; // Different from main server

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Servir les fichiers statiques (HTML, CSS, JS)
app.use(express.static(path.join(__dirname, 'public')));

// Email transporter
const transporter = nodemailer.createTransport({
    service: 'gmail',
    auth: {
        user: process.env.EMAIL_USER,
        pass: process.env.EMAIL_PASS
    }
});

// Store pending requests
const pendingRequests = new Map();
const requestsFilePath = path.join(__dirname, 'license_requests.json');

// Charger les demandes sauvegardées
function loadRequests() {
    try {
        if (fs.existsSync(requestsFilePath)) {
            const data = fs.readFileSync(requestsFilePath, 'utf8');
            return JSON.parse(data);
        }
    } catch (error) {
        console.error('Erreur chargement des demandes:', error);
    }
    return {};
}

// Sauvegarder les demandes
function saveRequests(requests) {
    try {
        fs.writeFileSync(requestsFilePath, JSON.stringify(requests, null, 2), 'utf8');
    } catch (error) {
        console.error('Erreur sauvegarde des demandes:', error);
    }
}

const savedRequests = loadRequests();

// Generate OTP
function generateOTP() {
    return Math.floor(10000000 + Math.random() * 90000000).toString(); // 8 digits
}

// Route pour la page d'accueil (formulaire)
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Route pour vérifier si l'utilisateur a déjà fait une demande
app.post('/check-request', (req, res) => {
    const { fingerprint } = req.body;
    
    if (!fingerprint) {
        return res.status(400).json({ error: 'Empreinte machine requise' });
    }
    
    const request = savedRequests[fingerprint];
    
    if (request) {
        res.json({
            hasRequest: true,
            userName: request.userName,
            userEmail: request.userEmail,
            requestDate: request.timestamp
        });
    } else {
        res.json({ hasRequest: false });
    }
});

// Routes
app.post('/request-license', async (req, res) => {
    console.log('📥 Requête de licence reçue:', req.body);
    try {
        const { userEmail, userName, idCard, fingerprint } = req.body;

        if (!userEmail || !userName || !idCard || !fingerprint) {
            return res.status(400).json({ error: 'Tous les champs sont requis' });
        }

        // Send request to admin
        const adminEmail = 'nyundumathryme@gmail.com';
        const mailOptions = {
            from: process.env.EMAIL_USER,
            to: adminEmail,
            subject: '🔐 Demande d\'autorisation de licence SETRAF',
            html: `
                <!DOCTYPE html>
                <html>
                <head>
                    <style>
                        body { font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px; }
                        .container { background-color: white; border-radius: 15px; padding: 40px; max-width: 600px; margin: 0 auto; box-shadow: 0 5px 20px rgba(0,0,0,0.1); }
                        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 30px; }
                        .info-table { width: 100%; border-collapse: collapse; margin: 20px 0; }
                        .info-table td { padding: 12px; border-bottom: 1px solid #eee; }
                        .info-table td:first-child { font-weight: bold; color: #667eea; width: 40%; }
                        .fingerprint { font-family: monospace; font-size: 11px; word-break: break-all; }
                        .btn { display: inline-block; background: linear-gradient(135deg, #66bb6a 0%, #43a047 100%); color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; margin: 20px 0; }
                        .footer { text-align: center; color: #999; font-size: 12px; margin-top: 30px; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h1>🔐 Nouvelle demande de licence</h1>
                            <p>SETRAF - Système de Gestion des Risques</p>
                        </div>

                        <p>Une nouvelle demande d'autorisation de licence a été reçue :</p>

                        <table class="info-table">
                            <tr>
                                <td>👤 Utilisateur</td>
                                <td>${userName}</td>
                            </tr>
                            <tr>
                                <td>📧 Email</td>
                                <td>${userEmail}</td>
                            </tr>
                            <tr>
                                <td>🆔 Carte d'identité</td>
                                <td>${idCard}</td>
                            </tr>
                            <tr>
                                <td>🖥️ Empreinte machine</td>
                                <td class="fingerprint">${fingerprint}</td>
                            </tr>
                        </table>

                        <div style="text-align: center;">
                            <a href="http://localhost:4000/admin.html" class="btn">
                                ✅ Gérer les demandes
                            </a>
                        </div>

                        <p style="color: #666; margin-top: 30px; font-size: 14px;">
                            <strong>Action requise :</strong> Cliquez sur le bouton ci-dessus pour accéder à l'interface d'administration 
                            et générer automatiquement le code de licence.
                        </p>

                        <div class="footer">
                            <p>© 2026 SETRAF</p>
                        </div>
                    </div>
                </body>
                </html>
            `
        };

        await transporter.sendMail(mailOptions);

        // Generate a request ID for tracking
        const requestId = crypto.randomBytes(8).toString('hex');
        
        // Sauvegarder la demande
        savedRequests[fingerprint] = {
            requestId,
            userName,
            userEmail,
            idCard,
            fingerprint,
            timestamp: new Date().toISOString(),
            status: 'pending'
        };
        saveRequests(savedRequests);
        
        res.json({
            success: true,
            message: 'Demande envoyée. Attendez l\'email d\'autorisation de SETRAF.',
            requestId
        });

    } catch (error) {
        console.error('Erreur:', error);
        res.status(500).json({ error: 'Erreur serveur' });
    }
});

app.post('/validate-license', async (req, res) => {
    try {
        const { fingerprint, licenseCode } = req.body;

        if (!fingerprint || !licenseCode) {
            return res.status(400).json({ error: 'Empreinte machine et code de licence requis' });
        }

        const request = savedRequests[fingerprint];
        if (!request) {
            return res.status(404).json({ error: 'Aucune demande trouvée pour cet appareil' });
        }

        // Créer le fichier de licence
        const licenseData = {
            user: request.userName,
            email: request.userEmail,
            fingerprint: fingerprint,
            licenseCode: licenseCode,
            activatedAt: new Date().toISOString()
        };

        const licenseFilePath = path.join(__dirname, 'license.key');
        fs.writeFileSync(licenseFilePath, JSON.stringify(licenseData, null, 2), 'utf8');

        // Mettre à jour le statut de la demande
        savedRequests[fingerprint].status = 'activated';
        savedRequests[fingerprint].activatedAt = new Date().toISOString();
        saveRequests(savedRequests);

        res.json({
            success: true,
            message: 'Licence activée avec succès! Vous pouvez maintenant redémarrer l\'application.'
        });

    } catch (error) {
        console.error('Erreur:', error);
        res.status(500).json({ error: 'Erreur serveur' });
    }
});

// Health check
app.get('/health', (req, res) => {
    res.json({ status: 'OK', pendingRequests: pendingRequests.size });
});

// Admin endpoints
app.get('/admin/requests', (req, res) => {
    res.json({ requests: savedRequests });
});

// Route pour envoyer le code de licence par email
app.post('/admin/send-license', async (req, res) => {
    try {
        const { fingerprint, email, userName, licenseCode } = req.body;

        if (!fingerprint || !email || !licenseCode) {
            return res.status(400).json({ error: 'Paramètres manquants' });
        }

        const request = savedRequests[fingerprint];
        if (!request) {
            return res.status(404).json({ error: 'Demande non trouvée' });
        }

        // Envoyer l'email avec le code de licence
        const mailOptions = {
            from: process.env.EMAIL_USER,
            to: email,
            subject: '🎉 Votre code de licence SETRAF',
            html: `
                <!DOCTYPE html>
                <html>
                <head>
                    <style>
                        body { font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px; }
                        .container { background-color: white; border-radius: 15px; padding: 40px; max-width: 600px; margin: 0 auto; box-shadow: 0 5px 20px rgba(0,0,0,0.1); }
                        .header { text-align: center; color: #667eea; margin-bottom: 30px; }
                        .code-box { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 25px; border-radius: 10px; text-align: center; font-size: 24px; font-weight: bold; letter-spacing: 2px; margin: 30px 0; }
                        .instructions { background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }
                        .instructions ol { margin-left: 20px; }
                        .instructions li { margin: 10px 0; line-height: 1.6; }
                        .footer { text-align: center; color: #999; font-size: 12px; margin-top: 30px; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h1>🎉 Félicitations ${userName} !</h1>
                            <p>Votre licence SETRAF a été approuvée</p>
                        </div>

                        <p>Votre demande de licence pour l'application SETRAF a été validée avec succès.</p>

                        <div class="code-box">
                            ${licenseCode}
                        </div>

                        <div class="instructions">
                            <h3>📋 Instructions d'activation :</h3>
                            <ol>
                                <li><strong>Copiez</strong> le code de licence ci-dessus</li>
                                <li><strong>Ouvrez</strong> votre navigateur sur <a href="http://localhost:4000">http://localhost:4000</a></li>
                                <li><strong>Collez</strong> le code dans le champ prévu à cet effet</li>
                                <li><strong>Cliquez</strong> sur "Activer la licence"</li>
                                <li><strong>Redémarrez</strong> l'application SETRAF</li>
                            </ol>
                        </div>

                        <p style="color: #666; margin-top: 20px;">
                            <strong>Note :</strong> Ce code est unique et lié à votre appareil. 
                            Ne le partagez avec personne.
                        </p>

                        <div class="footer">
                            <p>© 2026 SETRAF - Système de Gestion des Risques</p>
                            <p>Email : nyundumathryme@gmail.com</p>
                        </div>
                    </div>
                </body>
                </html>
            `
        };

        await transporter.sendMail(mailOptions);

        // Mettre à jour la demande avec le code de licence
        savedRequests[fingerprint].status = 'validated';
        savedRequests[fingerprint].licenseCode = licenseCode;
        savedRequests[fingerprint].validatedAt = new Date().toISOString();
        saveRequests(savedRequests);

        res.json({
            success: true,
            message: 'Code de licence envoyé par email',
            licenseCode
        });

    } catch (error) {
        console.error('Erreur envoi licence:', error);
        res.status(500).json({ error: 'Erreur lors de l\'envoi du code de licence' });
    }
});

app.post('/admin/validate', async (req, res) => {
    try {
        const { requestId } = req.body;

        const request = pendingRequests.get(requestId);
        if (!request) {
            return res.status(404).json({ error: 'Demande non trouvée' });
        }

        const validationCode = generateOTP() + request.fingerprint;
        const qrCodeDataURL = await qrcode.toDataURL(validationCode);

        // Send email to user with QR code
        const mailOptions = {
            from: process.env.EMAIL_USER,
            to: request.userEmail,
            subject: '🔐 Code de validation de licence SETRAF',
            html: `
                <h2>Validation de votre demande de licence SETRAF</h2>
                <p>Bonjour ${request.userName},</p>
                <p>Vos informations ont été validées par SETRAF.</p>
                <p>Scannez le QR code ci-dessous ou entrez le code manuellement :</p>
                <img src="${qrCodeDataURL}" alt="QR Code de validation" style="max-width: 200px;" />
                <p><strong>Code de validation :</strong> ${validationCode}</p>
                <p>Entrez ce code dans l'application pour activer votre licence.</p>
                <p>Cordialement,<br>Équipe SETRAF</p>
            `
        };

        if (transporter) {
            await transporter.sendMail(mailOptions);
        } else {
            console.log('📧 [TEST MODE] Validation email sent to:', request.userEmail);
            console.log('📧 Validation code:', validationCode);
            console.log('📧 QR Code URL:', qrCodeDataURL);
        }

        // Remove from pending
        pendingRequests.delete(requestId);

        res.json({
            success: true,
            message: 'Licence validée et envoyée à l\'utilisateur',
            validationCode
        });

    } catch (error) {
        console.error('Erreur validation:', error);
        res.status(500).json({ error: 'Erreur serveur' });
    }
});

app.listen(PORT, () => {
    console.log(`🚀 Serveur de licence démarré sur le port ${PORT}`);
    console.log(`📧 Email admin: nyundumathryme@gmail.com`);
    console.log(`🌐 Formulaire de demande disponible sur: http://localhost:${PORT}`);
    console.log(`📝 Les utilisateurs peuvent demander leur licence via le formulaire web`);
});