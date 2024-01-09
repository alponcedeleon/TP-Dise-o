(function($){
    function actualizarDepartamentos() {
        var selectedValue = $('#id_provincia').val();
        var api_url = 'https://apis.datos.gob.ar/georef/api/departamentos?provincia=' + selectedValue + '&max=1000';

        // Realiza la llamada a la API y actualiza las opciones del campo de departamento
        $.get(api_url, function(data){
            var departamentos = data.departamentos || [];
            var options = departamentos.map(function(depto){
                return { value: depto.nombre, display: depto.nombre };
            });

            // Limpia y actualiza las opciones del campo de departamento
            $('#id_departamento').empty();
            $.each(options, function(i, option){
                $('#id_departamento').append($('<option>', { value: option.value, text: option.display }));
            });

            // Desencadena el evento de cambio en el campo de departamento
            $('#id_departamento').trigger('change');
        });
    }

    // Captura el cambio en el campo de provincia
    
    // Llama a la función al cargar la página
    $(document).ready(function(){
        $('#id_provincia').change(actualizarDepartamentos);
        actualizarDepartamentos();
    });
})(django.jQuery);

/* (function($){
    function actualizarDepartamentos() {
        var selectedValue = $('#id_provincia').val();
        var api_url = 'https://apis.datos.gob.ar/georef/api/departamentos?provincia=' + selectedValue + '&max=1000';

        // Realiza la llamada a la API y actualiza las opciones del campo de departamento
        $.get(api_url, function(data){
            var departamentos = data.departamentos || [];
            var options = departamentos.map(function(depto){
                return { value: depto.nombre, display: depto.nombre };
            });

            // Limpia y actualiza las opciones del campo de departamento
            $('#id_departamento').empty();
            $.each(options, function(i, option){
                $('#id_departamento').append($('<option>', { value: option.value, text: option.display }));
            });
        });
    }

    // Captura el cambio en el campo de provincia
   

    // Llama a la función al cargar la página
    $(document).ready(function(){
        actualizarDepartamentos();
        $('#id_provincia').change(actualizarDepartamentos);
    });
})(django.jQuery); */
/* (function($){
    $(document).ready(function(){
        // Captura el cambio en el campo de provincia
        $('#id_provincia').change(function(){
            // Realiza la segunda llamada a la API basándote en la provincia seleccionada
            var selectedValue = $(this).val();
            var api_url = 'https://apis.datos.gob.ar/georef/api/departamentos?provincia=' + selectedValue + '&max=1000';

            // Actualiza las opciones del campo de departamento con los resultados de la API
            $.get(api_url, function(data){
                var departamentos = data.departamentos || [];
                var options = departamentos.map(function(depto){
                    return { value: depto.nombre, display: depto.nombre };
                });

                // Limpia y actualiza las opciones del campo de departamento
                $('#id_departamento').empty();
                $.each(options, function(i, option){
                    $('#id_departamento').append($('<option>', { value: option.value, text: option.display }));
                });
            });
        });
    });
})(django.jQuery); */