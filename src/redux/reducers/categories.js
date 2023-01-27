import {
    GET_CATEGORIES_SUCCESS,
    GET_CATEGORIES_FAIL,
} from '../actions/types';

const initialState = {
    categories: null
};

export default function Categories(state= initialState, action){
    const { type, payload }= action;

    switch(type){

        case GET_CATEGORIES_SUCCESS:                //UBICAMOS LA RESPUESTA POR EL TYPE ENVIADA POR ACTIONS
            return {
                ...state,
                categories: payload.categories      //EXTRAEMOS LA RESPUESTA EXACTA DEL ENVIO TIENE QUE VER CON EL VIEWS-RESP
            }
        case GET_CATEGORIES_FAIL:
            return {
                ...state,
                categories: null
            }    

        default:
            return state
    }


}