Ext._define('planning.hiring.minutesolicitation.MinuteSolicitationCommitmentNoteGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'planning.hiring.minutesolicitation.MinuteSolicitationCommitmentNoteWindow',

    configOrderToolBar: ['add', 'edit', 'remove', '-', 'reinforcement', 'reversal', '-', 'search'],

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Referente a NE', dataIndex: 'parent_unicode', width: 100},
                    {header: 'Número NE', dataIndex: 'number', width: 90},
                    {header: 'Valor (R$)', dataIndex: 'value', width: 90, 'renderer': toolkit.util.formatCurrency},
                    {header: 'Saldo', dataIndex: 'balance', width: 90, 'renderer': this.formatCurrency},
                    {header: 'Origem', dataIndex: 'origin_display', width: 120},
                    {header: 'Tipo', dataIndex: 'kind_display', width: 90},
                    {header: 'Contratado', dataIndex: 'provider_display', id: 'autoExpandColumn'},
                ]
            );

        return this._columnModel;
    },

    formatCurrency: function(value) {
        value = core.nullValue(value, 0);

        if (value === '-')
            return '<div style="text-align:right">-</div>';
        else
            return '<div style="text-align:right">' + Ext.util.Format.number(value, '0.0,00/i') + '</div>';
    },

    _requestReinforcement: function() {
        //Solicitando reforço
        this.reinforcementReversalWindow(100);
    },

    _requestReversal: function() {
        //Solicitando estorno
        this.reinforcementReversalWindow(1);
    },

    reinforcementReversalWindow: function(action) {
        var sel = this.getSelectionModel().getSelected();

        if(sel){
            if (sel.get('parent') == null){
                Ext._create('planning.hiring.minutesolicitation.MinuteSolicitationCommitmentNoteWindow', {
                    params: {
                        minute: this.params.minute,
                        parent: sel.get('pk'),
                        reinforcement_reversal: action,
                        solicitation: sel.get('solicitation'),
                        origin: sel.get('origin'),
                        kind: sel.get('kind'),
                        classification: sel.get('classification')
                    },
                    action: 'create',
                    callback: {
                    success: {
                        scope: this,
                        fn: function(args) {
                            this.getStore().reload();
                        }
                    }
                    },
                }).show();
            }else {
                Ext.Msg.show({
                    'title': 'Nota de Empenho',
                    'msg': 'Não posso solicitar reforço ou estorno para esta NE.',
                    'icon': Ext.Msg.WARNING,
                    'buttons': Ext.Msg.OK
                });
            }
        }else{
            Ext.Msg.show({
                'title': 'Nota de Empenho',
                'msg': 'Primeiro selecione a NE.',
                'icon': Ext.Msg.WARNING,
                'buttons': Ext.Msg.OK
            });
        }
    },

    getReinforcementAction: function() {
        if(!this._reinforcementAction)
            this._reinforcementAction = Ext._create('Ext.Button', {
                text: 'Solicitar Reforço',
                iconCls: 'icon-agree icon-agree-add',
                scope: this,
                handler: this._requestReinforcement
            });

        return this._reinforcementAction;
    },

    getReversalAction: function() {
        if(!this._reversalAction)
            this._reversalAction = Ext._create('Ext.Button', {
                text: 'Solicitar Estorno',
                iconCls: 'icon-agree icon-agree-list-remove',
                scope: this,
                handler: this._requestReversal
            });

        return this._reversalAction;
    },

    constructor: function(cfg) {
        cfg = (cfg ? cfg : {});

        Ext.applyIf(cfg, {
            columnAction: false,
            viewConfig: {
                scope: this,
                getRowClass: function(record) {
                    if(record.get('reinforcement_reversal') == 1) {
                        return 'x-grid3-red';
                    }
                    if(record.get('reinforcement_reversal') == 100) {
                        return 'x-grid3-green';
                    }
                }
            }
        });

        planning.hiring.minutesolicitation.MinuteSolicitationCommitmentNoteGrid.superclass.constructor.call(this, cfg);
    },
});

core.RestfulGrid.register(
    'planning.hiring.minutesolicitation.MinuteSolicitationCommitmentNoteRestful',
    'planning.hiring.minutesolicitation.MinuteSolicitationCommitmentNoteGrid'
);

