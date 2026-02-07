// App.tsx - Main application with routing
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, RequireAuth } from './context/AuthContext';
import { Landing } from './pages/Landing';
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { Dashboard } from './pages/Dashboard';
import { ModuleList } from './pages/ModuleList';
import { LearningModule } from './pages/LearningModule';
import { StudentLogin } from './pages/StudentLogin';
import { SelectProfile } from './pages/SelectProfile';
import { PrivacyPolicy } from './pages/PrivacyPolicy';
import { TeacherDashboard } from './pages/teacher/TeacherDashboard';
import { ModuleEditor } from './pages/teacher/ModuleEditor';
import { EducatorRoute } from './components/EducatorRoute';
import './App.css';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public routes */}
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={<Login />} />
          <Route path="/login-student" element={<StudentLogin />} />
          <Route path="/register" element={<Register />} />

          {/* Protected routes */}
          <Route
            path="/dashboard"
            element={
              <RequireAuth loginPath="/login-student">
                <Dashboard />
              </RequireAuth>
            }
          />
          <Route
            path="/modules"
            element={
              <RequireAuth loginPath="/login-student">
                <ModuleList />
              </RequireAuth>
            }
          />
          <Route
            path="/learn/:moduleId"
            element={
              <RequireAuth loginPath="/login-student">
                <LearningModule />
              </RequireAuth>
            }
          />
          <Route
            path="/select-profile"
            element={
              <RequireAuth loginPath="/login-student">
                <SelectProfile />
              </RequireAuth>
            }
          />
          <Route path="/privacy-policy" element={<PrivacyPolicy />} />

          {/* Teacher Routes */}
          <Route path="/teacher/*" element={
            <EducatorRoute>
              <Routes>
                <Route path="dashboard" element={<TeacherDashboard />} />
                <Route path="modules/new" element={<ModuleEditor />} />
                <Route path="modules/:moduleId/edit" element={<ModuleEditor />} />
                {/* Default for /teacher if no sub-path matches */}
                <Route index element={<Navigate to="dashboard" replace />} />
              </Routes>
            </EducatorRoute>
          } />

          {/* Catch all route - redirect to landing */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
