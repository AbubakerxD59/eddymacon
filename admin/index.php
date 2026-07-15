<?php
/**
 * /admin — login gate, then authenticated Command Center SPA.
 */

declare(strict_types=1);

require_once dirname(__DIR__) . '/backend/auth/session.php';

admin_session_start();

$error = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['logout'])) {
    admin_logout();
    header('Location: ' . strtok($_SERVER['REQUEST_URI'], '?'));
    exit;
}

if (!admin_is_authenticated() && $_SERVER['REQUEST_METHOD'] === 'POST') {
    $email = strtolower(trim((string) ($_POST['email'] ?? '')));
    $password = (string) ($_POST['password'] ?? '');

    /** @var array{email:string,password_hash:string} $auth */
    $auth = require dirname(__DIR__) . '/backend/config/auth.php';

    $ok = $email !== ''
        && $password !== ''
        && hash_equals(strtolower($auth['email']), $email)
        && password_verify($password, $auth['password_hash']);

    if ($ok) {
        admin_login($email);
        header('Location: ' . strtok($_SERVER['REQUEST_URI'], '?'));
        exit;
    }

    $error = 'Invalid email or password';
}

$authenticated = admin_is_authenticated();
?>
<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title><?= $authenticated ? 'Command Center' : 'Admin Login' ?> | EDDY MACON</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Playfair+Display:ital,wght@0,700;0,900;1,700;1,900&family=IBM+Plex+Mono:wght@400;700&display=swap" rel="stylesheet">
    <script>
      tailwind.config = {
        theme: {
          extend: {
            fontFamily: {
              sans: ['Inter', 'sans-serif'],
              serif: ['Playfair Display', 'serif'],
              mono: ['IBM Plex Mono', 'monospace'],
            },
            colors: {
              gold: {
                400: '#E5C158',
                500: '#D4AF37',
                600: '#C5A028',
                700: '#B8860B',
              },
              brand: {
                dark: '#020202',
                gray: '#0A0A0A',
                accent: '#111111',
                cyan: '#00F5FF',
                emerald: '#00FF41'
              }
            },
            maxWidth: {
              '8xl': '88rem',
            },
            animation: {
              'reveal-up': 'revealUp 1s cubic-bezier(0.16, 1, 0.3, 1) forwards',
            },
            keyframes: {
              revealUp: {
                '0%': { opacity: '0', transform: 'translateY(100px)' },
                '100%': { opacity: '1', transform: 'translateY(0)' },
              },
            }
          }
        }
      }
    </script>
    <style>
      body {
        background-color: #020202;
        color: #FFFFFF;
        overflow-x: hidden;
        -webkit-font-smoothing: antialiased;
      }
      .glass {
        background: rgba(2, 2, 2, 0.85);
        backdrop-filter: blur(24px);
        -webkit-backdrop-filter: blur(24px);
      }
      .gold-gradient {
        background: linear-gradient(135deg, #D4AF37 0%, #F9E79F 45%, #B8860B 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
      }
      /* Admin layout: no zoom on small screens; mild scale on large desktops */
      #root {
        font-size: 16px;
        zoom: 1;
      }
      @media (min-width: 1280px) {
        #root {
          zoom: 1.2;
          font-size: 16px;
        }
      }
      @media (min-width: 1536px) {
        #root {
          zoom: 1.35;
        }
      }
      .em-admin-shell {
        width: 100%;
        max-width: 100vw;
      }
      .em-admin-main {
        -webkit-overflow-scrolling: touch;
      }
      .no-scrollbar {
        -ms-overflow-style: none;
        scrollbar-width: none;
      }
      .no-scrollbar::-webkit-scrollbar {
        display: none;
      }
      /*
       * Full-viewport centered modal (Bootstrap-style).
       * Counteract #root zoom so fixed positioning uses the real viewport.
       */
      #root .em-admin-modal {
        zoom: 1;
        position: fixed !important;
        inset: 0 !important;
        width: 100vw !important;
        height: 100dvh !important;
        max-width: 100vw;
        max-height: 100dvh;
        margin: 0;
        display: flex !important;
        align-items: center;
        justify-content: center;
        padding: 0;
        box-sizing: border-box;
      }
      @media (min-width: 1280px) {
        #root .em-admin-modal {
          zoom: calc(1 / 1.2);
          width: 120vw !important;
          height: 120dvh !important;
        }
      }
      @media (min-width: 1536px) {
        #root .em-admin-modal {
          zoom: calc(1 / 1.35);
          width: 135vw !important;
          height: 135dvh !important;
        }
      }
      #root .em-admin-modal-dialog {
        width: min(48rem, 100vw);
        height: 100%;
        max-height: 100dvh;
        margin: 0 auto;
        display: flex;
        flex-direction: column;
      }
      #root .em-admin-drawer-backdrop,
      #root .em-admin-drawer {
        zoom: 1;
      }
      @media (min-width: 1280px) {
        #root .em-admin-drawer-backdrop,
        #root .em-admin-drawer {
          zoom: calc(1 / 1.2);
        }
      }
      @media (min-width: 1536px) {
        #root .em-admin-drawer-backdrop,
        #root .em-admin-drawer {
          zoom: calc(1 / 1.35);
        }
      }
      #root .em-admin-drawer {
        height: 100dvh;
      }
      #root input,
      #root textarea,
      #root button,
      #root label,
      #root p,
      #root span,
      #root h1,
      #root h2,
      #root h3,
      #root h4 {
        letter-spacing: normal;
      }
      @media (max-width: 639px) {
        #root .em-admin-header .tracking-widest {
          letter-spacing: 0.12em;
        }
      }
    </style>
<?php if ($authenticated): ?>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/toastr.js/latest/toastr.min.css" />
    <script>window.__ADMIN_AUTHENTICATED__ = true;</script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.7.1/jquery.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/toastr.js/latest/toastr.min.js"></script>
    <script>
      toastr.options = {
        closeButton: true,
        progressBar: true,
        positionClass: 'toast-top-right',
        timeOut: 4000,
      };
    </script>
    <script type="importmap">
    {
      "imports": {
        "lucide-react": "https://esm.sh/lucide-react@^0.562.0",
        "react/": "https://esm.sh/react@^19.2.3/",
        "react": "https://esm.sh/react@^19.2.3",
        "react-dom/": "https://esm.sh/react-dom@^19.2.3/",
        "@google/genai": "https://esm.sh/@google/genai@^1.35.0",
        "@supabase/supabase-js": "https://esm.sh/@supabase/supabase-js@2"
      }
    }
    </script>
    <script type="module" crossorigin src="../assets/index-Bpoe2-CA.js"></script>
<?php endif; ?>
  </head>
  <body>
<?php if ($authenticated): ?>
    <div id="root"></div>
<?php else: ?>
    <div class="fixed inset-0 z-[2000] bg-brand-dark flex items-center justify-center p-6">
      <div class="w-full max-w-md p-12 glass border border-gold-500/20 text-center space-y-10 animate-reveal-up relative z-10 rounded-sm shadow-2xl">
        <div class="text-gold-500 mx-auto w-12 h-12 flex items-center justify-center">
          <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
        </div>
        <h2 class="text-3xl font-serif font-black italic gold-gradient uppercase">Strategic Entry</h2>
        <?php if ($error !== ''): ?>
          <p class="text-red-400 text-xs uppercase tracking-widest font-bold"><?= htmlspecialchars($error, ENT_QUOTES, 'UTF-8') ?></p>
        <?php endif; ?>
        <form method="post" action="" class="space-y-6 text-left">
          <div class="space-y-2">
            <label class="block text-[10px] font-bold text-gray-500 uppercase tracking-widest">Email</label>
            <input
              type="email"
              name="email"
              required
              autocomplete="username"
              value="<?= htmlspecialchars((string) ($_POST['email'] ?? ''), ENT_QUOTES, 'UTF-8') ?>"
              class="w-full bg-brand-accent border-b-2 border-gold-500/30 py-3 px-2 text-white focus:outline-none focus:border-gold-500 text-sm"
              placeholder="Enter your email"
            />
          </div>
          <div class="space-y-2">
            <label class="block text-[10px] font-bold text-gray-500 uppercase tracking-widest">Password</label>
            <input
              type="password"
              name="password"
              required
              autocomplete="current-password"
              class="w-full bg-brand-accent border-b-2 border-gold-500/30 py-3 px-2 text-white focus:outline-none focus:border-gold-500 text-sm"
              placeholder="Enter your password"
            />
          </div>
          <button type="submit" id="em-login-btn" class="w-full bg-gold-500 text-black py-4 font-black uppercase tracking-widest hover:bg-white transition-all inline-flex items-center justify-center gap-2">
            <span id="em-login-label">Log In</span>
          </button>
        </form>
        <script>
          (function () {
            var form = document.querySelector('form[method="post"]');
            if (!form) return;
            form.addEventListener('submit', function () {
              var btn = document.getElementById('em-login-btn');
              var label = document.getElementById('em-login-label');
              if (!btn || btn.disabled) return;
              btn.disabled = true;
              btn.classList.add('opacity-70', 'cursor-wait');
              if (label) {
                label.textContent = 'Please wait...';
              }
              if (!document.getElementById('em-login-spinner')) {
                var sp = document.createElement('span');
                sp.id = 'em-login-spinner';
                sp.setAttribute('aria-hidden', 'true');
                sp.style.cssText = 'width:16px;height:16px;border:2px solid rgba(0,0,0,.25);border-top-color:#000;border-radius:50%;display:inline-block;animation:em-spin .7s linear infinite';
                btn.insertBefore(sp, label);
              }
            });
            var style = document.createElement('style');
            style.textContent = '@keyframes em-spin{to{transform:rotate(360deg)}}';
            document.head.appendChild(style);
          })();
        </script>
        <a href="../" class="inline-block text-[10px] uppercase tracking-widest text-gray-600 hover:text-gold-500 transition-colors">← Return to site</a>
      </div>
    </div>
<?php endif; ?>
  </body>
</html>
