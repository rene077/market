import{
    SIGNUP_SUCCESS,
    SIGNUP_FAIL,
    LOGIN_SUCCESS,
    LOGIN_FAIL,
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
    LOGOUT,
} from '../actions/types'

const initialState = {
    access: localStorage.getItem('access'),   //tomando desde el inspeccion los valores localStorage sí existen
    refresh: localStorage.getItem('refresh'),
    isAuthenticated: null,
    user: null,
    loading: false                //PARA SETEAR HABILITAR ICONO DE CARGA AL REALIZAR LLAMADO A LA API
}

//**CONTROLADOR.JS QUE ESPERA LA INFO DE AUTH.SERVICE -> VERIFICA SI ESTA TODO OK ADMINISTRA LA DATA**//
export default function Auth(state = initialState, action){        //STATE HEREDA TODO LOS CAMPOS DE "INITIAL STATE"
    const {type, payload} = action ;                               //ACTION HEREDA DE DISPATCH LAS VARIABLES
    
    switch(type){
        case SET_AUTH_LOADING:
            return{
                ...state,
                loading: true             //DEVOLVEMOS EL TRUE PARA MOSTRAR EL ICONO DE CARGA
            }   
        case REMOVE_AUTH_LOADING:
            return {
                ...state,
                loading: false            //DEVOLVEMOS EL FALSE PARA QUITAR EL ICONO DE CARGA  
            }  
        case USER_LOADED_SUCCESS:
            return {
                ...state,
                user: payload
            }    
        case USER_LOADED_FAIL:
            return {
                ...state,
                user: null
            }    
        case AUTHENTICATED_SUCCESS:
            return {
                ...state,
                isAuthenticated: true
            }    
        case AUTHENTICATED_FAIL:
            localStorage.removeItem('access');
            localStorage.removeItem('refresh');
            return {
                ...state,
                isAuthenticated: false,
                access: null,
                refresh: null,
            }    
        case LOGIN_SUCCESS:
            localStorage.setItem('access', payload.access);       
            localStorage.setItem('refresh', payload.refresh);
            return {
                ...state,
                isAuthenticated: true,
                access: localStorage.getItem('access'),
                refresh: localStorage.getItem('refresh')
            }


        case ACTIVATION_SUCCESS:
        case ACTIVATION_FAIL:
        case RESET_PASSWORD_SUCCESS:
        case RESET_PASSWORD_FAIL:
        case RESET_PASSWORD_CONFIRM_SUCCESS:
        case RESET_PASSWORD_CONFIRM_FAIL:                
            return{
                ...state
            }
            
        case REFRESH_SUCCESS:
            localStorage.setItem('access', payload.access);
            return {
                ...state,
                access: localStorage.getItem('access')
            }    

        case SIGNUP_SUCCESS:
        case SIGNUP_FAIL:
        case LOGIN_FAIL:
        case REFRESH_FAIL: 
        case LOGOUT:       
             localStorage.removeItem('access')
             localStorage.removeItem('refresh')
             return {
                ...state,
                access:null,
                refresh:null,
                isAuthenticated:false,
                user:null,
             }
        default:
            return state
    }
}