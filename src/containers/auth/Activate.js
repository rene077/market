import Layout from '../../hocs/Layout'
import { useParams } from 'react-router'
import { useState } from 'react'
import { connect } from 'react-redux'
import { activate } from '../../redux/actions/auth'
import { Navigate } from 'react-router'

import { Circles } from 'react-loader-spinner'

const Activate = ({
    activate,
    loading                     //AQUI SETEAMOS ,PARA PODER USAR LA VARIBLE DATA TRAIDA DE REDUX REDUCER
}) =>{
    const params = useParams()    
    const [activated, setActivated] = useState(false);   //VARIABLE CREADA PARA SABER SÍ SE ACTIVO LA CUENTA
                                                         //EL SET_ACTIVATED ES PARA PODER SETEAR TAL VARIABLE   
    const activate_account = () => {
        const uid = params.uid
        const token = params.token
        activate( uid, token);
        setActivated(true);
    }

    if(activated && !loading)                  //ACTIVATED TRUE, SIGNIFICA QUE YA ACCEDISTE A FUNCTION ACTIVATE_ACCOUNT()
    return <Navigate to='/'/>                  //ENTONCES TE ENVIA AL HOME "/"

    return (
        <Layout>
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                {/* We've used 3xl here, but feel free to try other max-widths based on your needs */}
                <div className="max-w-3xl mx-auto">
                
                {loading ?   //SÍ ES TRUE MUESTRA EL ICONO DE CARGA
                <button
                    className="inline-flex mt-12 items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  <Circles
                    color="#fff"
                    width={20}
                    height={20}
                  />  
                </button>:   //CASO CONTRARIO MUESTRA EL BUTTON DE AQUI ABAJO "ACTIVATE_ACCOUNT"
                <button
                onClick={ activate_account }
                className="inline-flex mt-12 items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                Activate Account
                </button>
                }
      
                </div>
            </div>
        </Layout>
    )
}

const mapStateToProps = state =>({
    loading: state.Auth.loading               //TOMAMOS LA VARIABLE O LA DATA DE QUE REDUCER EXPONE 
})

export default connect(mapStateToProps, {
    activate
})(Activate)