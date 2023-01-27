import{
    SIGNUP_SUCCESS,
    SIGNUP_FAIL,
    LOGIN_SUCCESS,
    LOGIN_FAIL,                      //TODAS ESTAS ETIQUETAS OR TYPES Y MÁS ,PODEMOS ENVIAR AL REDUCER CON DISPATCH()
    ACTIVATION_SUCCESS,
    ACTIVATION_FAIL,
    SET_AUTH_LOADING,
    REMOVE_AUTH_LOADING,
    USER_LOADED_SUCCESS,
    USER_LOADED_FAIL,
    AUTHENTICATED_SUCCESS,
    AUTHENTICATED_FAIL,
    REFRESH_SUCCESS,
    REFRESH_FAIL,
    RESET_PASSWORD_SUCCESS,
    RESET_PASSWORD_FAIL,
    RESET_PASSWORD_CONFIRM_SUCCESS,
    RESET_PASSWORD_CONFIRM_FAIL,
    LOGOUT
} from './types'
import { setAlert } from './alert';
import axios from 'axios'

export const check_authenticated = () => async dispatch => {
    if(localStorage.getItem('access')){
        const config = {
            headers: {
                'Accept': 'application/json',
                'Content-Type':'application/json'
            }
        };

        const body = JSON.stringify({
            token: localStorage.getItem('access') 
        });

        try{
            const res = await axios.post("http://localhost:8000/auth/jwt/verify/", body, config);
            
            if(res.status === 200){
                dispatch({
                    type: AUTHENTICATED_SUCCESS
                });
            } else {
                dispatch({
                    type: AUTHENTICATED_FAIL
                });
            }
        }catch(err){
            dispatch({
                type: AUTHENTICATED_FAIL
            });
        }
    } else {
        dispatch({
            type: AUTHENTICATED_FAIL
        });
    }
}

export const signup = (first_name, last_name, email, password, re_password) => async dispatch => {
    dispatch({
        type: SET_AUTH_LOADING               //HABILITAMOS ICONO DE CARGA  AL INICIAR UNA SOLICITUD
    })

    const config = {
            headers: {
                'Content-Type':'application/json'
            }
    };       

    const body = JSON.stringify({
        first_name,
        last_name,
        email,
        password,
        re_password
    });
    
    try {

       const res = await axios.post("http://127.0.0.1:8000/auth/users/", body, config);        
       //const res = await axios.post(`${process.env.REACT_APP_API_URL}/auth/users/`, body, config);
 
       if (res.status === 201){
          dispatch({  
              type: SIGNUP_SUCCESS,
              payload: res.data
          });
          dispatch(setAlert('Recibiras mail para activar.Reviza tu spam.','green'));
       } else {
          dispatch({
            type: SIGNUP_FAIL
          });
          dispatch(setAlert('Error al crear cuenta.','red'));
       }
       dispatch({
          type: REMOVE_AUTH_LOADING           //QUITAMOS EL ICONO DE CARGA AL ESTAR DEFINIDO EL RESULTADO SUCCESS O FAIL
       }) 


    } catch (err){
         dispatch({
            type: SIGNUP_FAIL
         });
         dispatch({
            type: REMOVE_AUTH_LOADING
         })
         dispatch(setAlert('Error conectando al servidor,intente mas tarde.','red'));
    }
};

//ESTA FUNCTION SERA USADA POR OTRA FUNCTION "LOGIN"//
export const load_user = () => async dispatch =>{
    if(localStorage.getItem('access')){          //LO TOMA AL ACCESS YA CARGADO POR LA FUNCTION LOGIN   
        const config = {
            headers : {
                'Authorization': `JWT ${localStorage.getItem('access')}`,
                'Accept': 'application/json'
            }
        };

        try{
            const res = await axios.get("http://127.0.0.1:8000/auth/users/me/", config);

            if( res.status === 200){
                dispatch({
                    type: USER_LOADED_SUCCESS,
                    payload: res.data
                })
            }else{
                dispatch({
                    type: USER_LOADED_FAIL
                })
            }

        }catch(err){
            dispatch({
                type: USER_LOADED_FAIL
            });
        }
    }else{
        dispatch({
            type: USER_LOADED_FAIL                            //EN CASO DE TENER EL ACCESS ES ERROR DE CARGA
        })
    }
}
//LOGIN CON EL EMAIL Y PASSWORD// Y USA LOAD PARA EXPONER DATOS DEL USUARIO//
export const login = (email, password) => async dispatch => {
    dispatch({
        type: SET_AUTH_LOADING                       //PARA MOSTRAR UN CARGADOR MIENTRAS EXISTE UN PROCESAMIENTO DE DATOS
    });

    const config = {
        headers: {
            'Content-Type': 'application/json'
        }                                            //ENVIO DE DATOS PERSONALES PARA LOGUEAR
    }

    const body = JSON.stringify({
        email,
        password
    })

    try{
        const res= await axios.post("http://127.0.0.1:8000/auth/jwt/create/", body, config);

        if(res.status === 200){
            dispatch({
                type: LOGIN_SUCCESS,
                payload: res.data
            })
            dispatch(load_user()) //SI ESTA TODO OK EL LOGIN, APLICAMOS FUNCTION QUE USA OTRA FUNCTION "SE USAN ENTRE SI" 
            dispatch({
                type: REMOVE_AUTH_LOADING                  //SACAMOS EL ICONO CARGADOR AL SALIR TODO OK
            });
            dispatch(setAlert('Inicio de sesion con éxito', 'green'));  //MOSTRAMOS MSN DE EXITO
        }else{
            dispatch({
                type: LOGIN_FAIL
            });
            dispatch({
                type: REMOVE_AUTH_LOADING
            });
            dispatch(setAlert('Error al iniciar sesion.', 'red'));
        }    

    }catch(err){
        dispatch({
            type: LOGIN_FAIL
        })
        dispatch({
            type:REMOVE_AUTH_LOADING
        })
        dispatch(setAlert('Error al iniciar sesion.Intente mas tarde', 'red'));
    }

}

export const activate = (uid, token)=> async dispatch =>{
    dispatch({
        type: SET_AUTH_LOADING
    });

    const config = {
        headers: {
            'Content-Type': 'application/json'
        }
    };

    const body = JSON.stringify({
        uid,
        token
    });

    try{
        const res = await axios.post("http://127.0.0.1:8000/auth/users/activation/", body, config); 
        
        if( res.status === 204 ){
            dispatch({
                type: ACTIVATION_SUCCESS
            });
            dispatch(setAlert('Cuenta activada correctamente', 'green'));
        }else{
            dispatch({
                type: ACTIVATION_FAIL
            });
            dispatch(setAlert('Error activando cuenta', 'red'));
        }
        dispatch({
            type:REMOVE_AUTH_LOADING
        });

    }
    catch(err){
          dispatch({
            type: ACTIVATION_FAIL
          });
          dispatch({
            type: REMOVE_AUTH_LOADING
          });
          dispatch(setAlert('Error al conectar al Servidor, intente mas tarde', 'red'));
    }

};

export const refresh = () => async dispatch => {
    if (localStorage.getItem('refresh')) {
        const config = {
            headers : {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        };
        const body = JSON.stringify({
            refresh: localStorage.getItem('refresh')
        })

        try{
            const res = await axios.post("http://127.0.0.1:8000/auth/jwt/refresh/", body, config);
            
            if(res.status === 200){
                dispatch({
                    type: REFRESH_SUCCESS,
                    payload: res.data
                });
            } else {
                dispatch({
                    type: REFRESH_FAIL
                });
            }
        }catch(err){
            dispatch({
                type: REFRESH_FAIL
            });
        }

    } else {
        dispatch({
            type: REFRESH_FAIL
        });
    }
}

export const reset_password = (email) => async dispatch => {
    dispatch({
        type: SET_AUTH_LOADING
    });

    const config = {
        headers : {
            'Content-Type':'application/json'
        }
    };

    const body = JSON.stringify({ email });

    try{
        const res = await axios.post("http://127.0.0.1:8000/auth/users/reset_password/", body , config);

        if( res.status === 204){
            dispatch({
                type: RESET_PASSWORD_SUCCESS
            });
            dispatch({
                type: REMOVE_AUTH_LOADING
            });
            dispatch(setAlert('Password reset email sent', 'green'));
        } else {
            dispatch({
                type: RESET_PASSWORD_CONFIRM_FAIL
            });
            dispatch({
                type: REMOVE_AUTH_LOADING
            });
            dispatch(setAlert('Error sending password reset email', 'red'));
        }

    }catch(err){
        dispatch({
            type: RESET_PASSWORD_FAIL
        });
        dispatch({
            type: REMOVE_AUTH_LOADING
        });
        dispatch(setAlert('Error sending password reset email', 'red'))
    }

}

export const reset_password_confirm = (uid, token, new_password, re_new_password) => async dispatch => {
    dispatch({
        type: SET_AUTH_LOADING
    });

    const config = {
        headers: {
            'Content-Type': 'application/json'
        } 
    };

    const body = JSON.stringify({
        uid,
        token,
        new_password,
        re_new_password
    })

    if(new_password !== re_new_password){
        dispatch({
            type: RESET_PASSWORD_CONFIRM_FAIL
        });
        dispatch({
            type: REMOVE_AUTH_LOADING
        });
        dispatch(setAlert('Passwords do not match', 'red'))
    }else{
        try{
            const res = await axios.post("http://127.0.0.1:8000/auth/users/reset_password_confirm/", body, config);

            if( res.status === 204){
                dispatch({
                    type: RESET_PASSWORD_CONFIRM_SUCCESS
                });
                dispatch({
                    type: REMOVE_AUTH_LOADING
                });
                dispatch(setAlert('Password has been reset successfully', 'green'));
            }else{
                dispatch({
                    type: RESET_PASSWORD_CONFIRM_FAIL
                });
                dispatch({
                    type: REMOVE_AUTH_LOADING
                });
                dispatch(setAlert('Error resetting your password', 'red'))
            }
        }catch(err){
            dispatch({
                type: RESET_PASSWORD_CONFIRM_FAIL
            });
            dispatch({
                type: REMOVE_AUTH_LOADING
            });
            dispatch(setAlert('Error resetting your password', 'red'));
        }
    }

}

export const logout = () => dispatch => {
    dispatch({
        type: LOGOUT
    });
    dispatch(setAlert('Successfully logged out', 'green'));
}  