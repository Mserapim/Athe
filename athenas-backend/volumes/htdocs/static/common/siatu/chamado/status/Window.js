/**
 *
 **/
Ext._define('common.siatu.chamado.status.Window', {
    extend: 'core.RestfulWindow',

    rest: 'common.siatu.chamado.status.Restful',

    // width: 360,
    width: 270,

    getStatusField: function(){
        if(!this._status){
            this._status = Ext._create('Ext.form.ComboBox',{
                fieldLabel: 'Status',
                hiddenName: 'status',
                width: 240,
                allowBlank: false,
                triggerAction: 'all',
                store: [
                        [3, 'Em atendimento','icon-siatu icon-siatu-atendimento'],
                        [8, 'Em Viagem','icon-siatu icon-siatu-viagem'],
                        [6, 'Terceirizada','icon-siatu icon-siatu-terceirizada'],
                        [7, 'Garantia','icon-siatu icon-siatu-garantia'],
                        [10, 'Aguardando entrega','icon-siatu icon-siatu-entrega'],
                        [11, 'Em manutenção','icon-siatu icon-siatu-manutencao'],
                        [4, 'Concluído','icon-siatu icon-siatu-concluido'], //Status  '4 - Aguardando avaliacao' representado como concluido para atendente
                    ],
                tpl: '<tpl for="."><div class="x-combo-list-item {field3}" style="height: 13px;">&nbsp &nbsp &nbsp &nbsp{' +
                    'field2'+ '}</div></tpl>',
            });

            this._status.on({
                scope: this,
                select: function(combo,record,index) {
                    if(record.get('field2')=='Terceirizada'){
                        this.getTerceirizadaField().enable();
                        this.getTerceirizadaField().show();
                    }
                    else{
                        this.getTerceirizadaField().disable();
                        this.getTerceirizadaField().hide();
                    }

                    if(record.get('field2')=='Garantia' || record.get('field2')=='Em Viagem' || record.get('field2')=='Terceirizada'){
                        this.getPrevisaoFimField().enable().show();
                    }
                    else{
                        this.getPrevisaoFimField().disable().hide();
                    }
                }
            });
        }

        return this._status;
    },

    getTerceirizadaField: function(){
        if(!this._terceirizada){
            this._terceirizada = Ext._create('core.fields.AutocompleteField', {
                rest: 'common.siatu.terceirizada.Restful',
                name: 'terceirizada',
                fieldLabel: 'Terceirizada',
                displayField: 'nome',
                allowBlank: false,
                hidden: this.values.status_display != 'Terceirizada',
                disabled: this.values.status_display != 'Terceirizada',
                gridConfig:{
                    columnAction: false,
                    allowUpdate: false,
                    allowRemove: false,
                    listeners:{
                        render: function(grid) {
                            tbar = grid.getToolbar();
                            tbar.remove(tbar.getComponent(1)); //Editar
                            tbar.remove(tbar.getComponent(1)); //Remover
                        }
                    }
                }
            });
        }

        return this._terceirizada;
    },

    getObservacaoField: function(){
        if(!this._observacao){
            this._observacao = Ext._create('Ext.form.TextField', {
                name: 'motivo',
                fieldLabel: 'Observação',
                width: 225,
            });
        }

        return this._observacao;
    },

    getPrevisaoFimField: function() {
        if(!this._previsao){
            this._previsao = Ext._create('Ext.form.DateField', {
                fieldLabel: 'Previsão de fim',
                name: 'previsao_fim',
                allowBlank: true,
                hidden: true,
                disabled: true,
            });
        }

        return this._previsao;
    },

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                labelAlign: 'top',
                items: [
                    this.getStatusField(),
                    this.getTerceirizadaField(),
                    this.getPrevisaoFimField(),
                    this.getObservacaoField(),

                ]
            });

        return this._formPanel;
    },

    setParam: function(key, value) {
        this.params = core.nullValue(this.params, {});
        this.params[key] = value;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        if (cfg.values)
            this.values = cfg.values;
        else{
            this.values = {};
        }

        Ext.applyIf(
            cfg,
            {
            }
        );

        Ext.apply(
            cfg,
            {
            }
        );
        common.siatu.chamado.status.Window.superclass.constructor.call(this, cfg);

        if(this.values.status_display == 'Garantia' || this.values.status_display == 'Terceirizada' || this.values.status_display == 'Em Viagem'){
            this.getPrevisaoFimField().enable().show();
        }
        if(this.action=='create'){
            this.setParam('insert',true);
        }
        else {
            delete this.params['insert'];
        }
    }
});
