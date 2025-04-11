/**
 *
 **/
Ext._define('edocs.processo.excluirWindow', {
    extend: 'core.RestfulWindow',

    rest: 'edocs.processo.Restful',

    width: 550,

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                labelWidth: 55,
                labelAlign: 'top',
                items: [
                    new toolkit.plugins.CKEditor({
                        name:'motivo_excluido',
                        fieldLabel:'Motivo',
                        toolbar: [
                            ['PasteFromWord'],
                            ['Link','Unlink','Anchor'],
                            ['NumberedList','BulletedList'],
                            ['Bold','Italic','Underline', 'Styles','Format', 'TextColor','BGColor']
                        ],
                        autoScroll:true,
                        width:520,
                        height: 215
                    })
                ]
            });

        return this._formPanel;
    }
});