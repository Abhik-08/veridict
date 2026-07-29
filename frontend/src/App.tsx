import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import { RootLayout } from '@/layouts'
import { HomePage, Login, Register, ForgotPassword } from '@/pages'
import { ProtectedRoute } from '@/components/Auth/ProtectedRoute'

const router = createBrowserRouter([
  {
    element: (
      <ProtectedRoute>
        <RootLayout />
      </ProtectedRoute>
    ),
    children: [
      {
        path: '/',
        element: <HomePage />,
      },
    ],
  },
  {
    path: '/login',
    element: <Login />,
  },
  {
    path: '/register',
    element: <Register />,
  },
  {
    path: '/forgot-password',
    element: <ForgotPassword />,
  },
])

export default function App() {
  return <RouterProvider router={router} />
}
