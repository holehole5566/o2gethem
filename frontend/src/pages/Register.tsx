import { useState } from "react";
import { useForm } from "react-hook-form";
import { register as registerApi } from "../services/api";
import { useApi } from "../hooks/useApi";

interface FormData {
  username: string;
  email: string;
  password: string;
}

export default function Register() {
  const [isRegistered, setIsRegistered] = useState(false);
  const { register, handleSubmit, formState: { errors } } = useForm<FormData>();
  const { execute, loading, error } = useApi();

  const onSubmit = async (data: FormData) => {
    try {
      const result = await execute(() => registerApi(data.username, data.email, data.password));
      if (result.status === "ok") {
        setIsRegistered(true);
      }
    } catch (err) {
      // Error handled by useApi hook
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
          
          <button type="submit" disabled={loading}>
            {loading ? "Creating account..." : "Register"}
          </button>
        </form>
      ) : (
        <div className="form">
          <p>Your account has been created successfully!</p>
        </div>
      )}
      {error && <div className="message error">{error}</div>}
      {isRegistered && <div className="message success">Account created successfully!</div>}
    </div>
  );
}
