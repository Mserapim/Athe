/**
 *
 **/
Ext._define('edocs.processo.justificativa.Window', {
    extend: 'core.RestfulWindow',

    rest: 'edocs.processo.justificativa.Restful',

    width: 550,

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                labelWidth: 70,
                items: this.get_items()
            });

        return this._formPanel;
    },

    get_items: function() {
        var items = [];
        items.push({
            width: 445,
            name: "codigo_processo",
            fieldLabel: "Processo",
            xtype: "textfield",
            readOnly: true,
        });
        if (this.params.tipo == 1) {
            items.push({
                width: 445,
                xtype: 'numberfield',
                name: 'paginas',
                fieldLabel: 'Página',
                allowBlank: false,
            });
        }
        if (this.params.tipo == 2) {
            items.push({
                width: 445,
                allowBlank: false,
                xtype: "textfield",
                name: "volume",
                maxLenght: 255,
                fieldLabel: "Volume",
                value: 'I',
                // regex: "^[a-zA-Z_]*$",
                regex: /^[mdclxviMDCLXVI]*$/,
                regexText: "<b>Erro:</b></br>Favor utilizar algarismos romanos.",
                validator: function(v) {
                    return /^[mdclxviMDCLXVI]*$/.test(v)?true:"Favor utilizar algarismos romanos";
                }
            });
        }
        items.push({
            xtype: 'ckeditor',
            name:'justificativa',
            fieldLabel:'Justificativa',
            toolbar: [
                ['PasteFromWord'],
                ['NumberedList','BulletedList'],
                ['Bold','Italic','Underline', 'Styles','Format', 'TextColor','BGColor']
            ],
            autoScroll:true,
            width:445,
            height:145
        })
        return items;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        this.params = cfg.params;

        edocs.processo.justificativa.Window.superclass.constructor.call(this, cfg);
    }
});
