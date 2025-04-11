/**
 *
 **/
Ext._define('auth.UserRestful', {
    'extend': 'core.Restful',

    'resource': 'AUTHUserRestful',

    'getFields': function() {
        if(!this._fields)
            this._fields = auth.UserRestful.superclass.getFields.call(this).concat([
                {'name': 'icons', 'type': 'auto'},
                {'name': 'username', 'type': 'string'},
                {'name': 'first_name', 'type': 'string'},
                {'name': 'last_name', 'type': 'string'},
                {'name': 'email', 'type': 'string'},
                {'name': 'is_active', 'type': 'bool'},
                {'name': 'is_staff', 'type': 'bool'},
                {'name': 'is_superuser', 'type': 'bool'},
                {'name': 'servidor', 'type': 'int', useNull: true},
                {'name': 'servidor_ativo', 'type': 'bool'},
                {'name': 'servidor_unicode', 'type': 'string'},
                {'name': 'servidor_matricula', 'type': 'string'},
                {'name': 'pessoa_nome_real', 'type': 'string'},
                {'name': 'pessoa_nome', 'type': 'string'}
            ]);

        return this._fields;
    }
});