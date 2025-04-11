/**
 *
 **/
Ext._define('common.siatu.BaseConhecimento.Window', {
    extend: 'core.RestfulWindow',

    rest: 'common.siatu.BaseConhecimento.Restful',

    width: 675,

    getCombo: function() {
        if(!this._combo) {
            if (Ext.util.Cookies.get('siatu-area-informatica') != null)
                this.filtroInformatica = Ext.decode(Ext.util.Cookies.get('siatu-area-informatica'));
            else
                this.filtroInformatica = false;
            this._combo = Ext._create('core.fields.AutocompleteField', {
                rest: 'common.siatu.BaseConhecimento.objeto.Restful',
                fieldLabel: 'Objeto',
                hiddenName: 'objeto',
                name: 'objeto',
                lazyRender: true,
                lazyInit: true,
                displayField: 'descricao',
                width: 250,
                preFilter: [{property: 'informatica', value: this.filtroInformatica, stage: 1000}],
                comboListeners: {
                    scope: this,
                    change: function(combo, newValue, oldValue){
                        this.getComboModelo().reset()
                        this.getComboModelo().getStore().load({});
                    },
                    changevalid:function(combo, id, start, valid) {
                        if(valid == true){
                            if(combo.getValue() != this.OldValueCmbObjeto){
                                console.debug('change VALID')
                                this.OldValueCmbObjeto = combo.getValue()
                                this.getComboModelo().setPreFilter([
                                    {property: 'objetos',value: combo.getValue(), stage: 0},
                                ])
                            }
                        }
                    },
                },
                gridConfig: {
                    allowUpdate: false,
                    hideItemsToolbar: ['edit', 'remove', 'download']
                }
            });
        }
        return this._combo;
    },

    getComboModelo: function() {
        if(!this._cmbModelo) {
            this._cmbModelo = Ext._create('core.fields.ComboField', {
                rest: 'common.siatu.BaseConhecimento.modelo.Restful',
                fieldLabel: 'Modelo',
                hiddenName: 'modelo',
                name: 'modelo',
                lazyRender: true,
                lazyInit: true,
                displayField: 'descricao',
                width: 250,
            });
        }

        return this._cmbModelo;
    },

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                labelWidth: 60,
                items: [
                    this.getCombo(),
                    this.getComboModelo(),
                    {
                        xtype: 'textarea',
                        name: 'problema',
                        fieldLabel: 'Problema',
                        allowBlank: false,
                        width: 580,
                        height: 40,
                    },
                    {
                        layout:'form',
                        labelAlign: 'top',
                        items:[
                            {
                                xtype: 'ckeditor',
                                name: 'solucao',
                                fieldLabel: 'Solução (4000 caracteres)',
                                toolbar: [
                                    ['Source'], ['PasteFromWord'], ['Scayt'],
                                    ['Link','Unlink','Anchor'],
                                    ['NumberedList','BulletedList'],
                                    ['Bold','Italic','Underline', 'Styles','Format', 'TextColor','BGColor']
                                ],
                                autoScroll: true,
                                width: 645,
                                height: 175
                            },
                           ]
                       },
                    {
                        fieldLabel: 'Arquivo',
                        name: 'arquivo',
                        hiddenName: 'arquivo',
                        xtype: 'ged-fileuploadfield',
                        allowBlank: true,
                        width: 250,
                    }
                ]
            });

        return this._formPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        this.action = cfg.action;

        common.siatu.BaseConhecimento.Window.superclass.constructor.call(this, cfg);

        if (this.action != 'update'){
            this.getComboModelo().setPreFilter([
                {property: 'objetos',value: null, stage: 0}
            ])
        }
    }
});
