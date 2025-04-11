Ext._define('rh.employeeaccesscontrol.authemployee.Window', {
    extend: 'rh.employee.Window',

    rest: 'rh.employeeaccesscontrol.authemployee.Restful',

    width: 550,

    save: function() {
        var values =  this.getFormPanel().getForm().getValues();
        Ext.Ajax.request({
            url: core.callAction('AUTHEmployeeRestful', 'create_or_update_username'),
            scope: this,
            params: Ext.apply(
                values,
                {
                    employee_id: this.oId,
                }
            ),
            success: function(xhr) {
                var rst = Ext.decode(xhr.responseText);
                var message, tipo;

                if(rst.success) {
                    message = 'Configurações persistidas com sucesso';
                    tipo = Ext.Msg.INFO;
                }
                else {
                    tipo = Ext.Msg.ERROR;
                    message = rst.message;
                }

                Ext.Msg.show({
                    title: 'Gravando configurações',
                    icon: tipo,
                    buttons: Ext.Msg.OK,
                    msg: message
                });
            }
        });
    },

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                border: false,
                items: [
                    {
                        xtype: 'textfield',
                        name: 'username',
                        fieldLabel: 'Usuário'
                    },
                    {
                        boxLabel: 'Ativo',
                        xtype: 'checkbox',
                        name: 'is_active',
                        fieldLabel: ''
                    },
                    {
                        boxLabel: 'Membro da Equipe',
                        xtype: 'checkbox',
                        name: 'is_staff',
                        fieldLabel: ''
                    },
                    {
                        boxLabel: 'Administrador do Sistema',
                        xtype: 'checkbox',
                        name: 'is_superuser',
                        fieldLabel: ''
                    }
                ],

            });

        return this._formPanel;
    },
});