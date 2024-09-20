def insert_school(connection, json_data: dict):
    insert_query = """
        INSERT INTO school_info (
            ordering, id_codmod, anexo, estrellitas_count, estrellitas, 
            cod_local, cen_edu, dir_cen, d_gestion, 
            pension, anio_pension, d_region, d_prov, d_dist, 
            estudiantes_x_aula, d_nivel, d_turno, TIPOSEXO_IE, d_alumnado, 
            nlat_ie, nlong_ie, identicole_estado, d_estado, fecha_creacion, 
            codigo_ubigeo, d_modalidad, i_modalidad, i_nivel, d_nivelDescripcion, 
            tiene_vacante, participa_vacante
        ) VALUES (
            %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, 
            %s
        );
    """
    cursor = connection.cursor()
    # Prepare the data from the JSON
    data_tuple = (
        json_data["ordering"],
        json_data["id_codmod"],
        json_data["anexo"],
        json_data["estrellitas_count"],
        json_data.get("estrellitas", None),  # Handle NULL values
        json_data["cod_local"],
        json_data["cen_edu"],
        json_data["dir_cen"],
        json_data["d_gestion"],
        json_data["pension"],
        json_data["anio_pension"],
        json_data["d_region"],
        json_data["d_prov"],
        json_data["d_dist"],
        json_data["estudiantes_x_aula"],
        json_data["d_nivel"],
        json_data["d_turno"],
        json_data["TIPOSEXO_IE"],
        json_data["d_alumnado"],
        json_data["nlat_ie"],
        json_data["nlong_ie"],
        json_data["identicole_estado"],
        json_data["d_estado"],
        json_data["fecha_creacion"],
        json_data["codigo_ubigeo"],
        json_data["d_modalidad"],
        json_data["i_modalidad"],
        json_data["i_nivel"],
        json_data["d_nivelDescripcion"],
        json_data["tiene_vacante"],
        json_data["participa_vacante"],
    )
    # Execute the query
    cursor.execute(insert_query, data_tuple)
    connection.commit()
