import { useState } from "react";
import { useForm } from "react-hook-form";
import { register as registerApi } from "../services/api";

interface FormData {
  username: string;
  email: string;
  password: string;
}

export default function Register() {
  const [msg, setMsg] = useState("");
  const [isRegistered, setIsRegistered] = useState(false);
  const { register, handleSubmit, formState: { errors } } = useForm<FormData>();

  const onSubmit = async (data: FormData) => {
    try {
      const result = await registerApi(data.username, data.email, data.password);
      if (result.status === "ok") {
        setMsg("Account created successfully!");
        setIsRegistered(true);
      } else {
        setMsg(result.message || "Registration failed");
      }
    } catch (err: any) {
      console.log(err);
      if (err.status === 409) {
        setMsg(err.message || "Username or email already exists");
      } else if (err.status === 400) {
        setMsg("Please fill in all required fields");
      } else {
        setMsg("Registration failed. Please try again.");
      }
    }
  };

  return (
    <div className="page-container">
      <h2>{isRegistered ? "Registration Successful!" : "Create Account"}</h2>
      {!isRegistered ? (
        <form onSubmit={handleSubmit(onSubmit)} className="form">
          <input 
            placeholder="Username" 
            {...register("username", { required: "Username is required" })} 
          />
          {errors.username && <span style={{color: 'red', fontSize: '0.8rem'}}>{errors.username.message}</span>}
          
          <input 
            placeholder="Email" 
            {...register("email", { 
              required: "Email is required",
              pattern: { value: /^[^@]+@[^@]+\.[^@]+$/, message: "Invalid email format" }
            })} 
          />
          {errors.email && <span style={{color: 'red', fontSize: '0.8rem'}}>{errors.email.message}</span>}
          
          <input 
            placeholder="Password" 
            type="password" 
            {...register("password", { 
              required: "Password is required",
              minLength: { value: 6, message: "Password must be at least 6 characters" }
            })} 
          />
          {errors.password && <span style={{color: 'red', fontSize: '0.8rem'}}>{errors.password.message}</span>}
          
          <button type="submit">Register</button>
        </form>
      ) : (
        <div className="form">
          <p>Your account has been created successfully!</p>
        </div>
      )}
      {msg && <div className={`message ${isRegistered ? 'success' : 'error'}`}>{msg}</div>}
    </div>
  );
}
