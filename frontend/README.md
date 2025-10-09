# Stock Advisor AI - Frontend

A modern, sleek Next.js frontend for the Stock Advisor AI system. Built with React, TypeScript, and Tailwind CSS.

## Features

- 🤖 **AI Chat Interface**: Interactive chat with the Stock Advisor AI agent
- 📊 **Portfolio Visualization**: Beautiful portfolio displays with performance metrics
- 🎯 **Stock Management**: Add, remove, and manage custom stocks
- 💰 **Capital-Aware Optimization**: Real-time portfolio recommendations
- 📱 **Responsive Design**: Works perfectly on desktop and mobile
- ⚡ **Fast Performance**: Built with Next.js 14 and optimized for speed

## Tech Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Animations**: Framer Motion
- **Icons**: Lucide React
- **HTTP Client**: Axios

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Stock Advisor AI backend running on port 5000

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create environment file:
```bash
cp .env.example .env.local
```

3. Update the API URL in `.env.local` if needed:
```
NEXT_PUBLIC_API_URL=http://localhost:5000
```

4. Start the development server:
```bash
npm run dev
```

5. Open [http://localhost:3000](http://localhost:3000) in your browser.

### Build for Production

```bash
npm run build
npm start
```

## Project Structure

```
frontend/
├── app/
│   ├── globals.css          # Global styles and Tailwind imports
│   ├── layout.tsx           # Root layout component
│   └── page.tsx             # Main homepage
├── components/
│   ├── Header.tsx           # App header with branding
│   ├── ChatInterface.tsx    # AI chat interface
│   ├── PortfolioDisplay.tsx # Portfolio visualization
│   └── StockManager.tsx     # Custom stock management
├── lib/
│   ├── api.ts               # API client and types
│   └── utils.ts             # Utility functions
├── package.json
├── tailwind.config.js       # Tailwind configuration
├── tsconfig.json            # TypeScript configuration
└── next.config.js           # Next.js configuration
```

## Usage

### AI Chat
- Start conversations with the AI agent
- Ask for stock recommendations
- Add custom stocks using natural language
- Get portfolio analysis and insights

### Stock Management
- Add custom stocks to your portfolio
- Remove unwanted stocks
- View all custom stocks
- Use quick actions for popular stock sets

### Portfolio Analysis
- View detailed portfolio allocations
- See performance metrics and risk analysis
- Historical backtesting results
- Net returns after transaction costs

## API Integration

The frontend communicates with the Flask backend through RESTful APIs:

- `GET /health` - Health check
- `POST /api/init` - Initialize system
- `GET /api/clusters` - Get stock clusters
- `POST /api/recommend` - Get recommendations
- `POST /api/stocks/add` - Add custom stocks
- `POST /api/stocks/remove` - Remove custom stocks
- `GET /api/stocks/list` - List custom stocks
- `POST /api/stocks/clear` - Clear custom stocks

## Styling

The app uses a minimalistic design with:
- Clean, modern interface
- Consistent color palette
- Smooth animations and transitions
- Responsive grid layouts
- Accessible design patterns

## Deployment

### Vercel (Recommended)

1. Push your code to GitHub
2. Connect your repository to Vercel
3. Set environment variables in Vercel dashboard
4. Deploy automatically

### Other Platforms

The app can be deployed to any platform that supports Next.js:
- Netlify
- Railway
- Render
- AWS Amplify

## Environment Variables

- `NEXT_PUBLIC_API_URL`: Backend API URL (default: http://localhost:5000)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
