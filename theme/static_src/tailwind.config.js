/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
      '../../templates/**/*.html', // Templates do projeto principal
      '../../core/templates/**/*.html', // Templates do app 'core'
      '../../core/forms.py', // Arquivos de formulários que podem conter classes
      // Adicione aqui outros apps que usem templates ou definam classes
  ],
  theme: {
    extend: {},
  },
  plugins: [],
  darkMode: 'class',
}