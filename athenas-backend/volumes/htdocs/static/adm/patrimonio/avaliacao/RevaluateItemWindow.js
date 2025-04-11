/*
 *
 */

Ext._define('adm.patrimonio.avaliacao.RevaluateItemWindow', {
    extend: 'adm.patrimonio.avaliacao.ManualItemWindow',

    actionTitles: {
        create: 'Novo - Reavaliação',
        update: 'Editar - Reavaliação',
        remove: 'Remover - Reavaliação',
        read: 'Carregar - Reavaliação'
    },

    getPatrimonioField: function(cfg) {
        if(!this._patrimonioField) {
            this._patrimonioField = adm.patrimonio.avaliacao.RevaluateItemWindow.superclass.getPatrimonioField.call(this, cfg);

            this._patrimonioField.getComboField().on({
                scope: this,
                select: function(combo, data) {
                    this.getFormPanel().getForm().setValues({
                        conservacao: data.get('conservacao'),
                        valor_atual: data.get('valor_atual'),
                        residual: 0.0,
                    });
                }
            });
        }

        return this._patrimonioField;
    },

    getValorAvaliadoField: function(cfg) {
        if(!this._valorAvaliadoField)
            this._valorAvaliadoField = Ext._create('Ext.form.NumberField', {
                fieldLabel: 'Valor liquido',
                name: 'valor_avaliado',
                style: 'text-align:right',
                listeners: {
                    scope: this,
                    change: function(text, value) {
                        var total;

                        total = Number.parseFloat(this.getValorAtualField().getValue()) - Number.parseFloat(value);

                        this.getDepreciacaoField().setValue(total);
                    }
                }
            });

        return this._valorAvaliadoField;
    },

    getConservacaoField: function(cfg) {
        if(!this._conservacaoField)
            this._conservacaoField = Ext._create('standard.fields.ChoiceField', {
                fieldLabel: 'Conservação',
                name: 'conservacao',
                hiddenName: 'conservacao',
                choiceId: 'patrimonio.CONSERVATION',
                width: 160
            });

        return this._conservacaoField;
    },
});
