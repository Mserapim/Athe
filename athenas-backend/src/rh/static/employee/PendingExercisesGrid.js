/**
 *
 **/
Ext._define('rh.employee.PendingExercisesGrid', {
    extend: 'rh.employee.Grid',

    restWindow: 'rh.employee.PendingExercisesWindow',

    constructor: function (cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.apply(cfg, {
            situationMenuValue: [
                {
                    name: 'active',
                    checked: true,
                    value: true,
                },
                {
                    name: 'finished',
                    checked: false,
                    value: false,
                },
            ],
            typePossessionItems: [
                {
                    name: 'efective',
                    checked: false,
                    value: 'EFE',
                },
                {
                    name: 'comissioned',
                    checked: false,
                    value: 'CMS',
                },
                {
                    name: 'member',
                    checked: true,
                    value: 'MBR',
                },
                {
                    name: 'member2',
                    checked: true,
                    value: 'MBR2',
                },
                {
                    name: 'requested',
                    checked: false,
                    value: 'REQ',
                },
                {
                    name: 'requestedrex',
                    checked: false,
                    value: 'REX',
                },
                {
                    name: 'efecm',
                    checked: false,
                    value: 'ECM',
                },
                {
                    name: 'memel',
                    checked: true,
                    value: 'MEL',
                },
                {
                    name: 'memel2',
                    checked: true,
                    value: 'MEL2',
                },
                {
                    name: 'memcm',
                    checked: true,
                    value: 'MCM',
                },
                {
                    name: 'memcm2',
                    checked: true,
                    value: 'MCM2',
                },
                {
                    name: 'reqcm',
                    checked: false,
                    value: 'RCM',
                },
                {
                    name: 'efefc',
                    checked: false,
                    value: 'EFC',
                },
                {
                    name: 'reqfc',
                    checked: false,
                    value: 'RFC',
                },
                {
                    name: 'memlcm',
                    checked: true,
                    value: 'MEC',
                },
                {
                    name: 'memlcm2',
                    checked: true,
                    value: 'MEC2',
                },
                {
                    name: 'trainee',
                    checked: false,
                    value: 'EST',
                },
                {
                    name: 'aprentice',
                    checked: false,
                    value: 'JCA',
                },
                {
                    name: 'outsourced',
                    checked: false,
                    value: 'TCR',
                },
                {
                    name: 'voluntare',
                    checked: false,
                    value: 'VOL',
                },
                {
                    name: 'contracted',
                    checked: false,
                    value: 'CTR',
                },
                {
                    name: 'extern',
                    checked: false,
                    value: 'EXT',
                },
                {
                    name: 'efretired',
                    checked: false,
                    value: 'SAP',
                },
                {
                    name: 'mretired',
                    checked: false,
                    value: 'MAP',
                },
                {
                    name: 'employeexxx',
                    checked: false,
                    value: 'XXX',
                },
            ]
        });
        rh.employee.PendingExercisesGrid.superclass.constructor.call(this, cfg);
    },
});

core.RestfulGrid.register(
    'rh.employee.PendingExercisesRestful',
    'rh.employee.PendingExercisesGrid'
);
