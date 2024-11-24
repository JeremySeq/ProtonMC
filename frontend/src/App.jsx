import Dashboard from './dashboard/Dashboard.jsx'
import Overview from './dashboard/Overview.jsx'
import Console from './dashboard/Console.jsx'
import Backups from './dashboard/Backups.jsx'
import Mods from './dashboard/Mods.jsx'
import ServerMenu from './ServerMenu'
import {
  createBrowserRouter,
  RouterProvider,
  redirect
} from "react-router-dom";
import LoginPage from './LoginPage';
import {hasAuth} from './AuthorizationHelper';
import ErrorPage from './ErrorPage'
import { NotificationProvider } from './NotificationContext';
import ServerCreator from "./ServerCreator.jsx";

function App() {
  const router = createBrowserRouter([
    {
      path: "/",
      loader() {
        if (hasAuth()) {
          return redirect("/servers");
        } else {
          return redirect("/login");
        }
      },
      errorElement: <ErrorPage></ErrorPage>
    },
    {
      path: "/login",
      element: <LoginPage></LoginPage>,
    },
    {
      path: "/servers",
      element: <ServerMenu></ServerMenu>,
      loader() {return protectedLoader()}
    },
    {
      path: "/create",
      element: <ServerCreator></ServerCreator>,
      loader() {return protectedLoader()}
    },
    {
      path: "/servers/:serverName",
      element: <Dashboard></Dashboard>,
      loader() {return protectedLoader()},
      children: [
        {
          path: "overview",
          element: <Overview></Overview>,
        },
        {
          path: "console",
          element: <Console></Console>,
        },
        {
          path: "backups",
          element: <Backups></Backups>,
        },
        {
          path: "mods",
          element: <Mods></Mods>
        }
      ]
    }
  ]);

  return (
    <>
      <NotificationProvider>
        <RouterProvider router={router} />
      </NotificationProvider>
    </>
  )
}


export default App

function protectedLoader() {
  if (hasAuth()) {
    return null;
  } else {
    return redirect("/login");
  }
}