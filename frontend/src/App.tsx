import './App.css'
import { SplineSceneBasic } from './components/home'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import {ChatMessageListDemo} from './components/chat';

function App() {
  return (
    <Router>
    <div className="max-h-screen bg-black-900 text-white p-8 flex flex-col items-center justify-center space-y-8">
      <Routes>
          <Route path="/" element={<SplineSceneBasic />} />
          <Route path="/chat" element={<ChatMessageListDemo />} />
        </Routes>
    </div>
    </Router>
  );
}

export default App;
