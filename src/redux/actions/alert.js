import {
    SET_ALERT,
    REMOVE_ALERT,
} from './types'
                    //ESTA FUNCTION SERA USADA EN OTRA FUNCTION "LOGIN Y OTRAS, COMO MSN DE EXITO O ERROR"
 export const setAlert = (msg, alertType, timeout = 5000) => dispatch => {
    dispatch({
        type: SET_ALERT,
        payload: { msg , alertType }
    });
     
    setTimeout(() => dispatch({ type: REMOVE_ALERT }), timeout);  //LUEGO DE 5 SEGS SE ENVIA EL REMOVE_ALERT AL REDUCER
}                                                                 //ENTONCES ALLI SE DARA LA ORDEN DE BORRAR EL ALERT              
  

