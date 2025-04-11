/**
 *
 **/

Ext._define('standard.classcode.Window', {
    extend: 'core.RestfulWindow',

    rest: 'standard.classcode.Restful',

    width: 600,

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                items: [
                    this.getClassCodePanel()
                ],
                // submit_all_checks: true
            });

        return this._formPanel;
    },

    getClassCodePanel: function() {
        if(!this._classCodePanel)
            this._classCodePanel = Ext._create('Ext.Panel', {
                frame: true,
                border: false,
                defaults: {
                    width: 400
                },
                // title: 'Geral',
                layout: 'form',
                items: [
                    {
                        fieldLabel: 'Título',
                        xtype: 'textfield',
                        name: 'title',
                        allowBlank: false
                    },{
                        fieldLabel: 'Path',
                        xtype: 'textfield',
                        name: 'path',
                        allowBlank: false
                    },{
                        fieldLabel: 'Slug',
                        xtype: 'textfield',
                        name: 'slug',
                        allowBlank: false
                    },{
                        fieldLabel: 'Objeto',
                        xtype: 'textfield',
                        name: 'name_object',
                        allowBlank: false
                    },{
                        fieldLabel: 'Descrição',
                        xtype: 'textfield',
                        name: 'description',
                        allowBlank: true
                    },{
                        fieldLabel: 'Tipo',
                        xtype: 'textfield',
                        name: 'typeof',
                        allowBlank: true,
                    },
                ]
            });

        return this._classCodePanel;
    }
});
